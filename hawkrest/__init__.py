import logging
import sys
import traceback

from django.conf import settings
from django.core.cache import cache

try:
    from django.utils.module_loading import import_string
except ImportError:
    # compatibility with django < 1.7
    from django.utils.module_loading import import_by_path
    import_string = import_by_path

from mohawk import Receiver
from mohawk.exc import HawkFail
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


log = logging.getLogger(__name__)
# Number of seconds until a Hawkmessage expires.
default_message_expiration = 60


class HawkAuthentication(BaseAuthentication):

    def authenticate(self, request):
        on_success = (DummyUser(), None)

        # In case there is an exception, tell others that the view passed
        # through Hawk authorization. The META dict is used because
        # middleware may not get an identical request object.
        # A dot-separated key is to work around potential environ var
        # pollution of META.
        request.META['hawk.receiver'] = None

        if getattr(settings, 'SKIP_HAWK_AUTH', False):
            # This was added as a convenient way to run the apk-signer
            # test suite but it's probably the wrong way to do it.
            log.warn('Hawk authentication disabled via settings')
            return on_success

        lookup_function = lookup_credentials
        settings_lookup_name = getattr(
            settings,
            'HAWK_CREDENTIALS_LOOKUP',
            None
        )
        if settings_lookup_name:
            lookup_function = import_string(settings_lookup_name)

        http_authorization = request.META.get('HTTP_AUTHORIZATION')
        if not http_authorization:
            log.debug('no authorization header in request')
            return None
        elif not http_authorization.startswith('Hawk '):
            log.debug('ignoring non-Hawk authorization header: {} '
                      .format(http_authorization))
            return None

        try:
            receiver = Receiver(
                lookup_function,
                http_authorization,
                request.build_absolute_uri(),
                request.method,
                content=request.body,
                seen_nonce=(seen_nonce
                            if getattr(settings, 'USE_CACHE_FOR_HAWK_NONCE',
                                       True)
                            else None),
                content_type=request.META.get('CONTENT_TYPE', ''),
                timestamp_skew_in_seconds=getattr(settings,
                                                  'HAWK_MESSAGE_EXPIRATION',
                                                  default_message_expiration))
        except HawkFail:
            etype, val, tb = sys.exc_info()
            log.debug(traceback.format_exc())
            raise AuthenticationFailed(
                'access denied: {etype.__name__}: {val}'
                .format(etype=etype, val=val)
            )

        # Pass our receiver object to the middleware so the request header
        # doesn't need to be parsed again.
        request.META['hawk.receiver'] = receiver
        return on_success


class DummyUser(object):
    pass


def lookup_credentials(cr_id):
    if cr_id not in settings.HAWK_CREDENTIALS:
        raise LookupError('No Hawk ID of {id}'.format(id=cr_id))
    return settings.HAWK_CREDENTIALS[cr_id]


def seen_nonce(id, nonce, timestamp):
    """
    Returns True if the Hawk nonce has been seen already.
    """
    key = '{id}:{n}:{ts}'.format(id=id, n=nonce, ts=timestamp)
    if cache.get(key):
        log.warning('replay attack? already processed nonce {k}'
                    .format(k=key))
        return True
    else:
        log.debug('caching nonce {k}'.format(k=key))
        cache.set(key, True,
                  # We only need the nonce until the message itself expires.
                  # This also adds a little bit of padding.
                  timeout=getattr(settings, 'HAWK_MESSAGE_EXPIRATION',
                                  default_message_expiration) + 5)
        return False

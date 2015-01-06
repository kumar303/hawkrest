import logging
import sys
import traceback

from django.conf import settings
from django.core.cache import cache

from mohawk import Receiver
from mohawk.exc import HawkFail
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


log = logging.getLogger(__name__)


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
            log.warn('Hawk authentication disabled via settings')
            return on_success

        if not request.META.get('HTTP_AUTHORIZATION'):
            log.debug('request did not send an Authorization header')
            raise AuthenticationFailed('missing authorization header')

        try:
            receiver = Receiver(
                lookup_credentials,
                request.META['HTTP_AUTHORIZATION'],
                request.build_absolute_uri(),
                request.method,
                content=request.body,
                seen_nonce=(seen_nonce
                            if getattr(settings, 'USE_CACHE_FOR_HAWK_NONCE',
                                       True)
                            else None),
                content_type=request.META.get('CONTENT_TYPE', ''),
                timestamp_skew_in_seconds=settings.HAWK_MESSAGE_EXPIRATION)
        except HawkFail:
            etype, val, tb = sys.exc_info()
            log.debug(traceback.format_exc())
            log.info('Hawk: denying access because of '
                     '{etype}: {val}'.format(etype=etype, val=val))
            raise AuthenticationFailed('authentication failed')

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


def seen_nonce(nonce, timestamp):
    """
    Returns True if the Hawk nonce has been seen already.
    """
    key = '{n}:{ts}'.format(n=nonce, ts=timestamp)
    if cache.get(key):
        log.warning('replay attack? already processed nonce {k}'
                    .format(k=key))
        return True
    else:
        log.debug('caching nonce {k}'.format(k=key))
        cache.set(key, True,
                  # We only need the nonce until the message itself expires.
                  # This also adds a little bit of padding.
                  timeout=settings.HAWK_MESSAGE_EXPIRATION + 5)
        return False

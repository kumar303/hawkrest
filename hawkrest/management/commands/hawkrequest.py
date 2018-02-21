import logging

from django.core.management.base import BaseCommand, CommandError
from mohawk import Sender

from hawkrest import HawkAuthentication


DEFAULT_HTTP_METHOD = 'GET'

CMD_OPTIONS = {
    '--url': {
        'action': 'store',
        'type': str,
        'help': 'Absolute URL to request.'
    },
    '--creds': {
        'action': 'store',
        'type': str,
        'help': 'ID for Hawk credentials.'
    },
    '-X': {
        'action': 'store',
        'type': str,
        'help': 'Request method. Default: {}.'.format(DEFAULT_HTTP_METHOD),
        'default': DEFAULT_HTTP_METHOD
    },
    '-d': {
        'action': 'store',
        'type': str,
        'help': 'Query string parameters.'
    }
}


def get_requests_module():
    import requests
    return requests


def request(url, method, data, headers):
    try:
        requests = get_requests_module()
    except ImportError:
        raise CommandError('To use this command you first need to '
                           'install the requests module')

    do_request = getattr(requests, method.lower())
    res = do_request(url, data=data, headers=headers)
    return res


def lookup_credentials(creds_key):
    return HawkAuthentication().hawk_credentials_lookup(creds_key)


class Command(BaseCommand):
    help = 'Make a Hawk authenticated request'

    def add_arguments(self, parser):
        for opt, config in CMD_OPTIONS.items():
            parser.add_argument(opt, **config)

    def handle(self, *args, **options):
        # Configure the mohawk lib for debug logging so we can see inputs to
        # the signature functions and other useful stuff.
        hawk_log = logging.getLogger('mohawk')
        hawk_log.setLevel(logging.DEBUG)
        hawk_log.addHandler(logging.StreamHandler())

        url = options['url']
        if not url:
            raise CommandError('Specify a URL to load with --url')

        creds_key = options['creds']
        if not creds_key:
            raise CommandError('Specify ID for Hawk credentials with --creds')

        method = options['X']
        qs = options['d'] or ''
        request_content_type = ('application/x-www-form-urlencoded'
                                if qs else 'text/plain')

        credentials = lookup_credentials(creds_key)

        sender = Sender(credentials,
                        url, method.upper(),
                        content=qs,
                        content_type=request_content_type)

        headers = {'Authorization': sender.request_header,
                   'Content-Type': request_content_type}

        res = request(url, method.lower(), data=qs, headers=headers)

        self.stdout.write('{method} -d {qs} {url}'.format(method=method.upper(),
                                                          qs=qs or 'None',
                                                          url=url))
        self.stdout.write(res.text)

        # Verify we're talking to our trusted server.
        self.stdout.write(str(res.headers))
        auth_hdr = res.headers.get('Server-Authorization', None)
        if auth_hdr:
            sender.accept_response(auth_hdr,
                                   content=res.text,
                                   content_type=res.headers['Content-Type'])
            self.stdout.write('<response was Hawk verified>')
        else:
            self.stdout.write('** NO Server-Authorization header **')
            self.stdout.write('<response was NOT Hawk verified>')

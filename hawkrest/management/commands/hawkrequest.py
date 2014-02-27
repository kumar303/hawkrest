from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

import logging
from mohawk import Sender

from hawkrest import lookup_credentials


class Command(BaseCommand):
    help = 'Make a Hawk authenticated request'
    option_list = BaseCommand.option_list + (
        make_option('--url', action='store', type=str,
                    help='Absolute URL to request.'),
        make_option('--creds', action='store', type=str,
                    help='ID for Hawk credentials.'),
        make_option('-X', action='store', type=str,
                    help='Request method. Default: %default.',
                    default='GET'),
        make_option('-d', action='store', type=str,
                    help='Query string parameters'),
    )

    def handle(self, *args, **options):
        hawk_log = logging.getLogger('mohawk')
        hawk_log.setLevel(logging.DEBUG)
        hawk_log.addHandler(logging.StreamHandler())

        try:
            import requests
        except ImportError:
            raise CommandError('To use this command you first need to '
                               'install the requests module')
        url = options['url']
        if not url:
            raise CommandError('Specify a URL to load with --url')

        qs = options['d'] or ''
        request_content_type = ('application/x-www-form-urlencoded'
                                if qs else 'text/plain')
        method = options['X']

        credentials = lookup_credentials(options['creds'])

        sender = Sender(credentials,
                        url, method.upper(),
                        content=qs,
                        content_type=request_content_type)

        headers = {'Authorization': sender.request_header,
                   'Content-Type': request_content_type}

        do_request = getattr(requests, method.lower())
        res = do_request(url, data=qs, headers=headers)

        print '{method} -d {qs} {url}'.format(method=method.upper(),
                                              qs=qs or 'None',
                                              url=url)
        print res.text

        # Verify we're talking to our trusted server.
        print res.headers
        auth_hdr = res.headers.get('Server-Authorization', None)
        if auth_hdr:
            sender.accept_response(auth_hdr,
                                   content=res.text,
                                   content_type=res.headers['Content-Type'])
            print '<response was Hawk verified>'
        else:
            print '** NO Server-Authorization header **'
            print '<response was NOT Hawk verified>'

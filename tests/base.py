from django.conf import settings
from django.test import RequestFactory, TestCase

from mohawk import Sender


class BaseTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = 'http://testserver/'
        self.credentials_id = 'script-user'
        self.credentials = settings.HAWK_CREDENTIALS[self.credentials_id]

    def _request(self, sender, method='GET', content_type='',
                 url=None, **kw):
        if not url:
            url = self.url

        do_request = getattr(self.factory, method.lower())
        return do_request(self.url,
                          HTTP_AUTHORIZATION=sender.request_header,
                          content_type=content_type,
                          # Django 1.7 no longer sets the header automatically
                          CONTENT_TYPE=content_type,
                          data=kw.pop('data', ''),
                          **kw)

    def _sender(self, method='GET', content_type='', url=None,
                credentials=None, content='', **kw):
        if not url:
            url = self.url
        if not credentials:
            credentials = self.credentials
        return Sender(credentials,
                      url, method,
                      content=content,
                      content_type=content_type,
                      **kw)

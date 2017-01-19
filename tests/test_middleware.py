from django.conf import settings
from django.http import HttpResponse

import mock
from mohawk.exc import MisComputedContentHash
from mohawk import Receiver

from hawkrest import lookup_credentials
from hawkrest.middleware import HawkResponseMiddleware

from .base import BaseTest


class TestMiddleware(BaseTest):

    def setUp(self):
        super(TestMiddleware, self).setUp()
        self.mw = HawkResponseMiddleware()

    def request(self, method='GET', content_type='text/plain', url=None):
        if not url:
            url = self.url
        sender = self._sender(method=method, content_type=content_type)
        req = self._request(sender, method=method, content_type=content_type)
        self.authorize_request(sender, req, url=url, method=method)

        return req, sender

    def authorize_request(self, sender, req, url=None, method='GET'):
        if not url:
            url = self.url
        # Simulate how a view authorizes a request.
        receiver = Receiver(lookup_credentials,
                            sender.request_header,
                            url, method,
                            content=req.body,
                            content_type=req.META['CONTENT_TYPE'])
        req.META['hawk.receiver'] = receiver

    def accept_response(self, response, sender):
        sender.accept_response(response['Server-Authorization'],
                               content=response.content,
                               content_type=response['Content-Type'])

    def test_respond_ok(self):
        req, sender = self.request()

        response = HttpResponse('the response')
        res = self.mw.process_response(req, response)
        self.accept_response(res, sender)

    def test_respond_with_bad_content(self):
        req, sender = self.request()

        response = HttpResponse('the response')
        res = self.mw.process_response(req, response)

        response.content = 'TAMPERED WITH'

        with self.assertRaises(MisComputedContentHash):
            self.accept_response(res, sender)

    def test_respond_with_bad_content_type(self):
        req, sender = self.request()

        response = HttpResponse('the response')
        res = self.mw.process_response(req, response)

        response['Content-Type'] = 'TAMPERED WITH'

        with self.assertRaises(MisComputedContentHash):
            self.accept_response(res, sender)

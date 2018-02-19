from django.test import RequestFactory

from tests.base import BaseTest
from hawkrest.util import get_auth_header, is_hawk_request


class TestGetAuthHeader(BaseTest):

    def test_func_gets_http_authorization_header(self):
        sender = self._sender()
        factory_obj = RequestFactory(HTTP_AUTHORIZATION=sender.request_header)
        request = factory_obj.request()
        auth_header = get_auth_header(request)
        self.assertEqual(auth_header, sender.request_header)

    def test_func_returns_empty_string_if_no_auth_header(self):
        factory_obj = RequestFactory()
        request = factory_obj.request()
        auth_header = get_auth_header(request)
        self.assertEqual(auth_header, '')


class TestIsHawkRequest(BaseTest):

    def test_func_returns_true_when_auth_header_begins_with_hawk(self):
        factory_obj = RequestFactory(HTTP_AUTHORIZATION='Hawk ')
        request = factory_obj.request()
        self.assertTrue(is_hawk_request(request))

    def test_func_returns_false_if_no_trailing_whitespace(self):
        factory_obj = RequestFactory(HTTP_AUTHORIZATION='Hawk')
        request = factory_obj.request()
        self.assertFalse(is_hawk_request(request))

    def test_func_returns_false_if_auth_header_missing(self):
        factory_obj = RequestFactory()
        request = factory_obj.request()
        self.assertFalse(is_hawk_request(request))

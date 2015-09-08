from django.conf import settings
from django.test.utils import override_settings

import mock
from nose.tools import eq_
from rest_framework.exceptions import AuthenticationFailed

from hawkrest import DummyUser, HawkAuthentication

from .base import BaseTest


ALTERNATIVE_CREDS = {
    'id' : 'alternative-id',
    'key' : 'other key',
    'algorithm' : 'sha256'
}


def alternative_lookup(cr_id):
    return ALTERNATIVE_CREDS


class AuthTest(BaseTest):

    def setUp(self):
        super(AuthTest, self).setUp()
        self.auth = HawkAuthentication()


class TestAuthentication(AuthTest):

    def test_www_authenticate_header(self):
        req = self.factory.get('/')
        eq_(self.auth.authenticate_header(req), 'Hawk')

    def test_no_auth_for_missing_header(self):
        req = self.factory.get('/')
        eq_(self.auth.authenticate(req), None)

    def test_no_auth_for_alternate_auth_scheme(self):
        # If the request contains another authorization scheme then it will
        # defer to your chain of validators.
        req = self.factory.get('/', HTTP_AUTHORIZATION='UnicornAuth: magic')
        eq_(self.auth.authenticate(req), None)

    def test_hawk_get(self):
        sender = self._sender()
        req = self._request(sender)
        assert isinstance(self.auth.authenticate(req)[0], DummyUser), (
            'Expected a successful authentication returning a dummy user')

    def test_hawk_post(self):
        post_data = 'one=1&two=2&three=3'
        content_type = 'application/x-www-form-urlencoded'
        method = 'POST'
        sender = self._sender(content=post_data,
                              content_type=content_type,
                              method=method)
        req = self._request(sender,
                            content_type=content_type,
                            data=post_data,
                            method=method)

        assert isinstance(self.auth.authenticate(req)[0], DummyUser), (
            'Expected a successful authentication returning a dummy user')

    def test_hawk_post_wrong_sig(self):
        post_data = 'one=1&two=2&three=3'
        content_type = 'application/x-www-form-urlencoded'
        method = 'POST'
        sender = self._sender(content=post_data,
                              content_type=content_type,
                              method=method)

        # This should fail the signature check.
        post_data = '{0}&TAMPERED_WITH=true'.format(post_data)

        req = self._request(sender,
                            content_type=content_type,
                            data=post_data,
                            method=method)

        self.assertRaisesRegexp(
            AuthenticationFailed,
            'access denied: MacMismatch: .*',
            lambda: self.auth.authenticate(req))

    def test_hawk_get_wrong_sig(self):
        sender = self._sender(url='http://realsite.com')
        req = self._request(sender, url='http://FAKE-SITE.com')

        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(req)

    def test_unknown_creds(self):
        wrong_creds = {'id': 'not-a-valid-id',
                       'key': 'not really',
                       'algorithm': 'sha256'}

        sender = self._sender(credentials=wrong_creds)
        req = self._request(sender)

        self.assertRaisesRegexp(
            AuthenticationFailed,
            'access denied: CredentialsLookupError: .*',
            lambda: self.auth.authenticate(req))

    def test_alternative_credential_lookup(self):
        sender = self._sender(credentials=ALTERNATIVE_CREDS)
        req = self._request(sender)
        lookup_path = "%s.alternative_lookup" % __name__
        with self.settings(HAWK_CREDENTIALS_LOOKUP=lookup_path):
            assert isinstance(self.auth.authenticate(req)[0], DummyUser), (
                'Expected a successful authentication returning a dummy user')


class TestNonce(AuthTest):

    def setUp(self):
        super(TestNonce, self).setUp()
        p = mock.patch('hawkrest.cache')
        self.cache = p.start()
        self.addCleanup(p.stop)

    def auth_request(self):
        sender = self._sender()
        req = self._request(sender)
        self.auth.authenticate(req)

    def test_check_nonce_ok(self):
        self.cache.get.return_value = False
        self.auth_request()
        assert self.cache.get.called, 'nonce should have been checked'

    def test_store_nonce(self):
        self.cache.get.return_value = False
        self.auth_request()
        assert self.cache.set.called, 'nonce should have been cached'

    def test_nonce_exists(self):
        self.cache.get.return_value = True
        self.assertRaisesRegexp(
            AuthenticationFailed,
            'access denied: AlreadyProcessed: Nonce.*',
            self.auth_request)

    def test_disabled(self):
        with self.settings(USE_CACHE_FOR_HAWK_NONCE=False):
            self.auth_request()
        assert not self.cache.get.called, 'nonce check should be disabled'

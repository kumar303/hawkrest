from django.conf import settings

import mock
from nose.tools import eq_
from rest_framework.exceptions import AuthenticationFailed

from hawkrest import DummyUser, HawkAuthentication

from .base import BaseTest

class AlternativeLookupAuthentication(HawkAuthentication):

    CREDS = {
        'id' : 'alternative-id',
        'key' : 'other key',
        'algorithm' : 'sha256'
    }

    def lookup_credentials(self, cr_id):
        return self.CREDS

class AuthTest(BaseTest):

    def setUp(self):
        super(AuthTest, self).setUp()
        self.auth = HawkAuthentication()


class TestAuthentication(AuthTest):

    def test_missing_auth_header(self):
        req = self.factory.get('/')
        with self.assertRaises(AuthenticationFailed) as exc:
            self.auth.authenticate(req)

        eq_(exc.exception.detail, 'missing authorization header')

    def test_bad_auth_header(self):
        req = self.factory.get('/', HTTP_AUTHORIZATION='not really')
        with self.assertRaises(AuthenticationFailed) as exc:
            self.auth.authenticate(req)

        eq_(exc.exception.detail, 'authentication failed')

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

        with self.assertRaises(AuthenticationFailed) as exc:
            self.auth.authenticate(req)

        eq_(exc.exception.detail, 'authentication failed')

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

        with self.assertRaises(AuthenticationFailed) as exc:
            self.auth.authenticate(req)

        eq_(exc.exception.detail, 'authentication failed')

    def test_alternative_credential_lookup(self):
        sender = self._sender(
            credentials=AlternativeLookupAuthentication.CREDS
        )
        req = self._request(sender)
        auth = AlternativeLookupAuthentication()
        assert isinstance(auth.authenticate(req)[0], DummyUser), (
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
        with self.assertRaises(AuthenticationFailed) as exc:
            self.auth_request()

        eq_(exc.exception.detail, 'authentication failed')

    def test_disabled(self):
        with self.settings(USE_CACHE_FOR_HAWK_NONCE=False):
            self.auth_request()
        assert not self.cache.get.called, 'nonce check should be disabled'

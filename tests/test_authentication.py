import re
import unittest

from django.conf import settings

try:
    # Importing via base_user avoids the need for `django.contrib.auth`
    # be added to `INSTALLED_APPS` in Django 1.9 and later.
    from django.contrib.auth.base_user import AbstractBaseUser
except ImportError:
    # For compatibility with Django 1.8 and earlier.
    from django.contrib.auth.models import AbstractBaseUser

import mock
from nose.tools import eq_
from rest_framework.exceptions import AuthenticationFailed

from hawkrest import HawkAuthenticatedUser, HawkAuthentication

from .base import BaseTest


ALTERNATIVE_CREDS = {
    'id' : 'alternative-id',
    'key' : 'other key',
    'algorithm' : 'sha256'
}

def alternative_cred_lookup(cr_id):
    return ALTERNATIVE_CREDS

class AlternateAuthentication(HawkAuthentication):
    def hawk_credentials_lookup(self, cr_id):
        return ALTERNATIVE_CREDS


class AlternateAuthenticatedUser(HawkAuthenticatedUser):
    pass

def alternative_user_lookup(request, credentials):
    return AlternateAuthenticatedUser(), None

class AlternateUserAuthentication(HawkAuthentication):
    def hawk_user_lookup(self, request, credentials):
        return AlternateAuthenticatedUser(), None
        

class AuthTest(BaseTest):

    def setUp(self):
        super(AuthTest, self).setUp()
        self.auth = HawkAuthentication()

        p = mock.patch('hawkrest.log')
        self.mock_log = p.start()
        self.addCleanup(p.stop)

    def assert_log_regex(self, method, pattern):
        log_call = getattr(self.mock_log, method).call_args[0][0]
        assert re.search(pattern, log_call), (
            'Expected log.{}() matching "{}", saw: "{}"'.format(method, pattern, log_call))


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
        assert isinstance(self.auth.authenticate(req)[0],
                          HawkAuthenticatedUser), (
            'Expected a successful authentication returning a user')

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

        assert isinstance(self.auth.authenticate(req)[0],
                          HawkAuthenticatedUser), (
            'Expected a successful authentication returning a user')

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

        self.assertRaisesRegexp(AuthenticationFailed,
                                '^Hawk authentication failed$',
                                lambda: self.auth.authenticate(req))
        self.assert_log_regex('warning', '^access denied: MisComputedContentHash: ')

    def test_hawk_get_wrong_sig(self):
        sender = self._sender(url='http://realsite.com')
        req = self._request(sender, url='http://FAKE-SITE.com')

        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(req)

    def test_bad_header(self):
        sender = self._sender()
        sender.request_header += ', ext="invalid header \t"'
        req = self._request(sender)

        self.assertRaisesRegexp(AuthenticationFailed,
                                '^Hawk authentication failed: The request header was ',
                                lambda: self.auth.authenticate(req))
        self.assert_log_regex('warning', '^access denied: BadHeaderValue: ')

    def test_unknown_creds(self):
        wrong_creds = {'id': 'not-a-valid-id',
                       'key': 'not really',
                       'algorithm': 'sha256'}

        sender = self._sender(credentials=wrong_creds)
        req = self._request(sender)

        self.assertRaisesRegexp(AuthenticationFailed,
                                '^Hawk authentication failed$',
                                lambda: self.auth.authenticate(req))
        self.assert_log_regex('warning',
                              '^access denied: CredentialsLookupError: ')

    def test_alternative_creds_lookup_setting(self):
        sender = self._sender(credentials=ALTERNATIVE_CREDS)
        req = self._request(sender)
        lookup_path = "%s.alternative_cred_lookup" % __name__
        with self.settings(HAWK_CREDENTIALS_LOOKUP=lookup_path):
            assert isinstance(self.auth.authenticate(req)[0],
                              HawkAuthenticatedUser), (
                'Expected a successful authentication returning a user')

    def test_alternative_creds_lookup_sublcass(self):
        auth = AlternateAuthentication()
        sender = self._sender(credentials=ALTERNATIVE_CREDS)
        req = self._request(sender)
        assert isinstance(auth.authenticate(req)[0],
                          HawkAuthenticatedUser), (
            'Expected a successful authentication returning a user')

    def test_alternative_user_lookup_setting(self):
        sender = self._sender()
        req = self._request(sender)
        lookup_path = "%s.alternative_user_lookup" % __name__
        with self.settings(HAWK_USER_LOOKUP=lookup_path):
            assert isinstance(self.auth.authenticate(req)[0],
                              AlternateAuthenticatedUser), (
                'Expected a successful authentication returning a user')

    def test_alternative_user_lookup_sublcass(self):
        auth = AlternateUserAuthentication()
        sender = self._sender()
        req = self._request(sender)
        assert isinstance(auth.authenticate(req)[0],
                          AlternateAuthenticatedUser), (
            'Expected a successful authentication returning a user')

    def test_expired_token(self):
        sender = self._sender(_timestamp="123")
        req = self._request(sender)

        self.assertRaisesRegexp(AuthenticationFailed,
                                '^Hawk authentication failed: The token has expired. Is ',
                                lambda: self.auth.authenticate(req))
        self.assert_log_regex('warning', '^access denied: TokenExpired: ')

    def test_get_user(self):
        assert isinstance(self.auth.get_user(None),
                          HawkAuthenticatedUser), (
            'Expected returning a user')


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
        self.assertRaisesRegexp(AuthenticationFailed,
                                '^Hawk authentication failed$',
                                self.auth_request)
        self.assert_log_regex('warning',
                              '^access denied: AlreadyProcessed: Nonce')

    def test_disabled(self):
        with self.settings(USE_CACHE_FOR_HAWK_NONCE=False):
            self.auth_request()
        assert not self.cache.get.called, 'nonce check should be disabled'


class TestHawkAuthenticatedUser(unittest.TestCase):

    def setUp(self):
        self.user = HawkAuthenticatedUser()

    def test_method_compliance(self):
        for name, attr in AbstractBaseUser.__dict__.items():
            # Skip private and capitalized callables (like __init__ or Meta)
            # Skip non-callable attributes.
            if (    name.startswith('_') or
                    name[0] == name[0].upper() or
                    not callable(attr)):
                continue
            if not getattr(self.user, name, None):
                raise AssertionError(
                    'HawkAuthenticatedUser is missing method: {}'
                    .format(name))

    def test_is_anonymous(self):
        eq_(self.user.is_anonymous(), False)

    def test_is_authenticated(self):
        eq_(self.user.is_authenticated(), True)

    def test_is_active(self):
        eq_(self.user.is_active, True)

    def test_has_usable_password(self):
        eq_(self.user.has_usable_password(), False)

import mock

from django.core.management.base import CommandError
from django.core.management import call_command
from requests.models import Response

from tests.base import BaseTest


def exec_cmd(**kwargs):
    call_command('hawkrequest', **kwargs)


class TestManagementCommand(BaseTest):

    @mock.patch('hawkrest.management.commands.hawkrequest.get_requests_module')
    def test_error_raised_if_requests_not_imported(self, mk_import):
        mk_import.side_effect = ImportError()
        with self.assertRaises(CommandError):
            exec_cmd(url=self.url, creds=self.credentials_id)

    def test_error_raised_if_url_not_specified(self):
        with self.assertRaises(CommandError):
            exec_cmd(creds=self.credentials_id)

    def test_error_raised_if_creds_missing(self):
        with self.assertRaises(CommandError):
            exec_cmd(url=self.url)

    def test_error_raises_if_creds_not_found(self):
        with self.assertRaises(CommandError):
            exec_cmd(creds='nonexistent')

    @mock.patch('hawkrest.management.commands.hawkrequest.request')
    @mock.patch('mohawk.Sender.accept_response')
    def test_response_unverified_without_auth_header(self, mk_accept, mk_resp):
        response = Response()
        response._content = b'Unauthorized'
        mk_resp.return_value = Response()
        exec_cmd(url=self.url, creds=self.credentials_id)
        self.assertFalse(mk_accept.called)

    @mock.patch('hawkrest.management.commands.hawkrequest.request')
    @mock.patch('mohawk.Sender.accept_response')
    def test_response_verified_with_auth_header(self, mk_accept, mk_resp):
        response = Response()
        response.headers['Server-Authorization'] = 'xyz'
        response.headers['Content-Type'] = 'text/plain'
        response._content = b'Authorized'
        mk_resp.return_value = response
        exec_cmd(url=self.url, creds=self.credentials_id)
        self.assertTrue(mk_accept.called)

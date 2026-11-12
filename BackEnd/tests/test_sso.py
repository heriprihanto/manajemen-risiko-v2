"""SSO boundary tests, using a dummy issuer; no database or live network."""
import unittest
from unittest.mock import patch

import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import UserDep, ensure_opd_access
from app.core.sso import session_request


class SsoTests(unittest.TestCase):
    def setUp(self):
        self.old = settings.SSO_ENABLED
        settings.SSO_ENABLED = True
        self.app = FastAPI()

        @self.app.get('/private')
        @self.app.post('/private')
        def private(user=UserDep):
            ensure_opd_access(user, 12)
            return user

        from app.routers.auth import router
        from app.db import get_session
        self.app.include_router(router)
        self.app.dependency_overrides[get_session] = lambda: None
        self.client = TestClient(self.app, base_url='https://testserver')
        self.client.cookies.set(settings.SSO_COOKIE_NAME, 'dummy-session')
        self.user = {'id': 'dummy-user', 'username': 'dummy', 'role_id': 9, 'id_opds': [12], 'nama': 'Dummy'}

    def tearDown(self):
        settings.SSO_ENABLED = self.old
        self.client.close()

    def issuer(self, status=200, data=None):
        response = httpx.Response(status, json=self.user if data is None else data)
        return patch('app.core.sso.httpx.Client', return_value=unittest.mock.MagicMock(
            __enter__=unittest.mock.Mock(return_value=unittest.mock.Mock(request=unittest.mock.Mock(return_value=response)))))

    def test_cookie_user_and_opd_mapping(self):
        with self.issuer():
            response = self.client.get('/private')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['opds'], [12])
        self.assertEqual(response.json()['display_name'], 'Dummy')

    def test_no_cookie_does_not_accept_local_bearer(self):
        self.client.cookies.clear()
        response = self.client.get('/private', headers={'Authorization': 'Bearer old-local-token'})
        self.assertEqual(response.status_code, 401)

    def test_revoked_expired_and_blocked(self):
        for status in (401, 403):
            with self.subTest(status=status), self.issuer(status):
                self.assertEqual(self.client.get('/private').status_code, status)

    def test_other_opd_is_denied(self):
        with self.issuer(data={**self.user, 'id_opds': [99]}):
            self.assertEqual(self.client.get('/private').status_code, 403)

    def test_unsafe_requests_require_exact_origin(self):
        for origin in (None, 'null', 'https://evil.example', settings.SSO_PUBLIC_ORIGIN + '.evil.example'):
            headers = {} if origin is None else {'Origin': origin}
            self.assertEqual(self.client.post('/private', headers=headers).status_code, 403)
        with self.issuer():
            self.assertEqual(self.client.post('/private', headers={'Origin': settings.SSO_PUBLIC_ORIGIN}).status_code, 200)

    def test_invalid_issuer_response_never_grants_access(self):
        for data in ({}, [], {**self.user, 'role_id': '1'}, {**self.user, 'id_opds': ['12']}):
            with self.subTest(data=data), self.issuer(data=data):
                self.assertEqual(self.client.get('/private').status_code, 503)
        with self.issuer(500):
            self.assertEqual(self.client.get('/private').status_code, 503)

    def test_issuer_unavailable(self):
        with patch('app.core.sso.httpx.Client', side_effect=httpx.ConnectError('dummy')):
            self.assertEqual(self.client.get('/private').status_code, 503)

    def test_standalone_login_is_disabled(self):
        response = self.client.post('/auth/login', json={'username': 'dummy', 'password': 'dummy'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.client.get('/auth/captcha').status_code, 404)
        self.assertTrue(self.client.get('/auth/config').json()['sso_enabled'])

    def test_logout_endpoint_clears_cookie_after_revocation(self):
        with self.issuer(204):
            response = self.client.post('/auth/logout', headers={'Origin': settings.SSO_PUBLIC_ORIGIN})
        self.assertEqual(response.status_code, 204)
        self.assertIn('Max-Age=0', response.headers['set-cookie'])
        self.assertEqual(response.headers['cache-control'], 'no-store')

    def test_me_is_not_cacheable(self):
        with self.issuer():
            response = self.client.get('/auth/me')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['cache-control'], 'no-store')

    def test_logout_calls_issuer_delete(self):
        from starlette.requests import Request
        request = Request({'type': 'http', 'headers': [(b'cookie', f'{settings.SSO_COOKIE_NAME}=dummy'.encode())]})
        with self.issuer(204):
            self.assertEqual(session_request(request, 'DELETE'), {})


if __name__ == '__main__':
    unittest.main()

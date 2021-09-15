from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from mayan.apps.common.tests import GenericViewTestCase
from mayan.apps.smart_settings.classes import Namespace
from mayan.apps.user_management.tests.literals import (
    TEST_CASE_USER_EMAIL, TEST_CASE_USER_PASSWORD, TEST_CASE_USER_USERNAME,
)

from ..settings import setting_maximum_session_length

from .literals import TEST_EMAIL_AUTHENTICATION_BACKEND


class UserLoginTestCase(GenericViewTestCase):
    """
    Test that users can login using the supported authentication methods
    """
    authenticated_url = '{}?next={}'.format(
        reverse(settings.LOGIN_URL), reverse(viewname='documents:document_list')
    )
    auto_login_user = False

    def setUp(self):
        super(UserLoginTestCase, self).setUp()
        Namespace.invalidate_cache_all()

    def _request_authenticated_view(self):
        return self.get(viewname='documents:document_list')

    @override_settings(AUTHENTICATION_LOGIN_METHOD='username')
    def test_normal_behavior(self):
        response = self._request_authenticated_view()
        self.assertRedirects(
            response=response, expected_url=self.authenticated_url
        )

    @override_settings(AUTHENTICATION_LOGIN_METHOD='username')
    def test_username_login(self):
        logged_in = self.login(
            username=TEST_CASE_USER_USERNAME, password=TEST_CASE_USER_PASSWORD
        )
        self.assertTrue(logged_in)
        response = self._request_authenticated_view()
        # We didn't get redirected to the login URL
        self.assertEqual(response.status_code, 200)

    @override_settings(AUTHENTICATION_LOGIN_METHOD='email')
    def test_email_login(self):
        with self.settings(AUTHENTICATION_BACKENDS=(TEST_EMAIL_AUTHENTICATION_BACKEND,)):
            logged_in = self.login(
                username=TEST_CASE_USER_USERNAME, password=TEST_CASE_USER_PASSWORD
            )
            self.assertFalse(logged_in)

            logged_in = self.login(
                email=TEST_CASE_USER_EMAIL, password=TEST_CASE_USER_PASSWORD
            )
            self.assertTrue(logged_in)

            response = self._request_authenticated_view()
            # We didn't get redirected to the login URL
            self.assertEqual(response.status_code, 200)

    @override_settings(AUTHENTICATION_LOGIN_METHOD='username')
    def test_username_login_via_views(self):
        response = self._request_authenticated_view()
        self.assertRedirects(
            response=response, expected_url=self.authenticated_url
        )

        response = self.post(
            viewname=settings.LOGIN_URL, data={
                'username': TEST_CASE_USER_USERNAME,
                'password': TEST_CASE_USER_PASSWORD
            }
        )
        response = self._request_authenticated_view()
        # We didn't get redirected to the login URL
        self.assertEqual(response.status_code, 200)

    @override_settings(AUTHENTICATION_LOGIN_METHOD='email')
    def test_email_login_via_views(self):
        with self.settings(AUTHENTICATION_BACKENDS=(TEST_EMAIL_AUTHENTICATION_BACKEND,)):
            response = self._request_authenticated_view()
            self.assertRedirects(
                response=response, expected_url=self.authenticated_url
            )

            response = self.post(
                viewname=settings.LOGIN_URL, data={
                    'email': TEST_CASE_USER_EMAIL, 'password': TEST_CASE_USER_PASSWORD
                }, follow=True
            )
            self.assertEqual(response.status_code, 200)

            response = self._request_authenticated_view()
            # We didn't get redirected to the login URL
            self.assertEqual(response.status_code, 200)

    @override_settings(AUTHENTICATION_LOGIN_METHOD='username')
    def test_username_remember_me(self):
        response = self.post(
            viewname=settings.LOGIN_URL, data={
                'username': TEST_CASE_USER_USERNAME,
                'password': TEST_CASE_USER_PASSWORD,
                'remember_me': True
            }, follow=True
        )

        response = self._request_authenticated_view()
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            self.client.session.get_expiry_age(),
            setting_maximum_session_length.value
        )
        self.assertFalse(self.client.session.get_expire_at_browser_close())

    @override_settings(AUTHENTICATION_LOGIN_METHOD='username')
    def test_username_dont_remember_me(self):
        response = self.post(
            viewname=settings.LOGIN_URL, data={
                'username': TEST_CASE_USER_USERNAME,
                'password': TEST_CASE_USER_PASSWORD,
                'remember_me': False
            }, follow=True
        )

        response = self._request_authenticated_view()
        self.assertEqual(response.status_code, 200)

        self.assertTrue(self.client.session.get_expire_at_browser_close())

    @override_settings(AUTHENTICATION_LOGIN_METHOD='email')
    def test_email_remember_me(self):
        with self.settings(AUTHENTICATION_BACKENDS=(TEST_EMAIL_AUTHENTICATION_BACKEND,)):
            response = self.post(
                viewname=settings.LOGIN_URL, data={
                    'email': TEST_CASE_USER_EMAIL,
                    'password': TEST_CASE_USER_PASSWORD,
                    'remember_me': True
                }, follow=True
            )

            response = self._request_authenticated_view()
            self.assertEqual(response.status_code, 200)

            self.assertEqual(
                self.client.session.get_expiry_age(),
                setting_maximum_session_length.value
            )
            self.assertFalse(self.client.session.get_expire_at_browser_close())

    @override_settings(AUTHENTICATION_LOGIN_METHOD='email')
    def test_email_dont_remember_me(self):
        with self.settings(AUTHENTICATION_BACKENDS=(TEST_EMAIL_AUTHENTICATION_BACKEND,)):
            response = self.post(
                viewname=settings.LOGIN_URL, data={
                    'email': TEST_CASE_USER_EMAIL,
                    'password': TEST_CASE_USER_PASSWORD,
                    'remember_me': False
                }
            )

            response = self._request_authenticated_view()
            self.assertEqual(response.status_code, 200)

            self.assertTrue(self.client.session.get_expire_at_browser_close())

    @override_settings(AUTHENTICATION_LOGIN_METHOD='username')
    def test_password_reset(self):
        response = self.post(
            viewname='authentication:password_reset_view', data={
                'email': TEST_CASE_USER_EMAIL,
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

        uid_token = mail.outbox[0].body.replace('\n', '').split('/')

        response = self.post(
            viewname='authentication:password_reset_confirm_view',
            args=uid_token[-3:-1], data={
                'new_password1': TEST_CASE_USER_PASSWORD,
                'new_password2': TEST_CASE_USER_PASSWORD,
            }
        )

        self.assertEqual(response.status_code, 302)

        self.login(
            username=TEST_CASE_USER_USERNAME, password=TEST_CASE_USER_PASSWORD
        )

        response = self._request_authenticated_view()
        self.assertEqual(response.status_code, 200)

    def test_username_login_redirect(self):
        TEST_REDIRECT_URL = reverse(viewname='common:about_view')

        response = self.post(
            path='{}?next={}'.format(
                reverse(settings.LOGIN_URL), TEST_REDIRECT_URL
            ), data={
                'username': TEST_CASE_USER_USERNAME,
                'password': TEST_CASE_USER_PASSWORD,
                'remember_me': False
            }, follow=True
        )

        self.assertEqual(response.redirect_chain, [(TEST_REDIRECT_URL, 302)])

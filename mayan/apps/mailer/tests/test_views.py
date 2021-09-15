from __future__ import unicode_literals

from django.core import mail

from mayan.apps.common.tests import GenericViewTestCase
from mayan.apps.documents.tests import GenericDocumentViewTestCase

from ..models import UserMailer
from ..permissions import (
    permission_mailing_link, permission_mailing_send_document,
    permission_user_mailer_create, permission_user_mailer_delete,
    permission_user_mailer_edit, permission_user_mailer_use,
    permission_user_mailer_view
)

from .literals import (
    TEST_EMAIL_ADDRESS, TEST_EMAIL_FROM_ADDRESS,
    TEST_RECIPIENTS_MULTIPLE_COMMA, TEST_RECIPIENTS_MULTIPLE_COMMA_RESULT,
    TEST_RECIPIENTS_MULTIPLE_MIXED, TEST_RECIPIENTS_MULTIPLE_MIXED_RESULT,
    TEST_RECIPIENTS_MULTIPLE_SEMICOLON,
    TEST_RECIPIENTS_MULTIPLE_SEMICOLON_RESULT, TEST_USER_MAILER_LABEL,
    TEST_USER_MAILER_LABEL_EDITED
)
from .mailers import TestBackend
from .mixins import MailerTestMixin


class MailerViewsTestCase(MailerTestMixin, GenericViewTestCase):
    def test_user_mailer_create_view_no_permissions(self):
        response = self._request_test_user_mailer_create()

        self.assertNotContains(
            response, text=TestBackend.label, status_code=403
        )
        self.assertEqual(UserMailer.objects.count(), 0)

    def test_user_mailer_create_view_with_permission(self):
        self.grant_permission(permission=permission_user_mailer_create)

        response = self._request_test_user_mailer_create()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(UserMailer.objects.count(), 1)

    def test_user_mailer_delete_view_no_permissions(self):
        self._create_user_mailer()

        response = self._request_test_user_mailer_delete()
        self.assertEqual(response.status_code, 404)

        self.assertQuerysetEqual(
            UserMailer.objects.all(), (repr(self.user_mailer),)
        )

    def test_user_mailer_delete_view_with_access(self):
        self._create_user_mailer()

        self.grant_access(
            obj=self.user_mailer, permission=permission_user_mailer_delete
        )

        response = self._request_test_user_mailer_delete()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(UserMailer.objects.count(), 0)

    def test_user_mailer_edit_view_no_permission(self):
        self._create_user_mailer()

        response = self._request_test_user_mailer_edit()
        self.assertEqual(response.status_code, 404)

        self.user_mailer.refresh_from_db()
        self.assertEqual(self.user_mailer.label, TEST_USER_MAILER_LABEL)

    def test_user_mailer_edit_view_with_access(self):
        self._create_user_mailer()

        self.grant_access(
            obj=self.user_mailer, permission=permission_user_mailer_edit
        )

        response = self._request_test_user_mailer_edit()
        self.assertEqual(response.status_code, 302)

        self.user_mailer.refresh_from_db()
        self.assertEqual(self.user_mailer.label, TEST_USER_MAILER_LABEL_EDITED)

    def test_user_mailer_list_view_no_permissions(self):
        self._create_user_mailer()

        response = self._request_test_user_mailer_list_view()
        self.assertNotContains(
            response, text=self.user_mailer.label, status_code=200
        )

    def test_user_mailer_list_view_with_access(self):
        self._create_user_mailer()

        self.grant_access(
            permission=permission_user_mailer_view, obj=self.user_mailer
        )
        response = self._request_test_user_mailer_list_view()

        self.assertContains(
            response, text=self.user_mailer.label, status_code=200
        )

    def test_user_mailer_test_view_no_permissions(self):
        self._create_user_mailer()

        response = self._request_test_user_mailer_test()

        self.assertEqual(response.status_code, 404)

        self.assertEqual(len(mail.outbox), 0)

    def test_user_mailer_test_view_with_access(self):
        self._create_user_mailer()

        self.grant_access(
            obj=self.user_mailer, permission=permission_user_mailer_use
        )

        response = self._request_test_user_mailer_test()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(mail.outbox[0].to, [TEST_EMAIL_ADDRESS])

    def test_send_multiple_recipients_comma(self):
        self._create_user_mailer()

        self.grant_access(
            obj=self.user_mailer, permission=permission_user_mailer_use
        )

        self.test_email_address = TEST_RECIPIENTS_MULTIPLE_COMMA
        response = self._request_test_user_mailer_test()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(
            mail.outbox[0].to, TEST_RECIPIENTS_MULTIPLE_COMMA_RESULT
        )

    def test_send_multiple_recipients_mixed(self):
        self._create_user_mailer()

        self.grant_access(
            obj=self.user_mailer, permission=permission_user_mailer_use
        )

        self.test_email_address = TEST_RECIPIENTS_MULTIPLE_MIXED
        response = self._request_test_user_mailer_test()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(
            mail.outbox[0].to, TEST_RECIPIENTS_MULTIPLE_MIXED_RESULT
        )

    def test_send_multiple_recipients_semicolon(self):
        self._create_user_mailer()

        self.grant_access(
            obj=self.user_mailer, permission=permission_user_mailer_use
        )

        self.test_email_address = TEST_RECIPIENTS_MULTIPLE_SEMICOLON
        response = self._request_test_user_mailer_test()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(
            mail.outbox[0].to, TEST_RECIPIENTS_MULTIPLE_SEMICOLON_RESULT
        )


class DocumentViewsTestCase(MailerTestMixin, GenericDocumentViewTestCase):
    def setUp(self):
        super(DocumentViewsTestCase, self).setUp()
        self.login_user()

    def _request_document_link_send(self):
        return self.post(
            viewname='mailer:document_send_link',
            kwargs={'document_id': self.document.pk},
            data={
                'email': getattr(
                    self, 'test_email_address', TEST_EMAIL_ADDRESS
                ),
                'user_mailer': self.user_mailer.pk
            }
        )

    def _request_document_send(self):
        return self.post(
            viewname='mailer:document_send',
            kwargs={'document_id': self.document.pk},
            data={
                'email': getattr(
                    self, 'test_email_address', TEST_EMAIL_ADDRESS
                ), 'user_mailer': self.user_mailer.pk
            }
        )

    def test_mail_link_view_no_permissions(self):
        self._create_user_mailer()

        response = self._request_document_link_send()

        self.assertNotContains(
            response=response, text=self.user_mailer.label, status_code=404
        )
        self.assertNotContains(
            response=response, text=self.document.label, status_code=404
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_mail_link_view_with_document_access(self):
        self._create_user_mailer()

        self.grant_access(
            permission=permission_mailing_link, obj=self.document
        )

        response = self._request_document_link_send()
        self.assertNotContains(
            response=response, text=self.user_mailer.label, status_code=200
        )
        self.assertContains(
            response=response, text=self.document.label, status_code=200
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_mail_link_view_with_mailer_access(self):
        self._create_user_mailer()

        self.grant_access(
            permission=permission_user_mailer_use, obj=self.user_mailer
        )

        response = self._request_document_link_send()
        self.assertNotContains(
            response=response, text=self.user_mailer.label, status_code=404
        )
        self.assertNotContains(
            response=response, text=self.document.label, status_code=404
        )

        self.assertEqual(len(mail.outbox), 0)

    def test_mail_link_view_with_full_access(self):
        self._create_user_mailer()

        self.grant_access(
            permission=permission_mailing_link, obj=self.document
        )
        self.grant_access(
            permission=permission_user_mailer_use, obj=self.user_mailer
        )

        response = self._request_document_link_send()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(mail.outbox[0].to, [TEST_EMAIL_ADDRESS])

    def test_mail_document_view_no_permissions(self):
        self._create_user_mailer()

        response = self._request_document_send()
        self.assertNotContains(
            response=response, text=self.user_mailer.label, status_code=404
        )
        self.assertNotContains(
            response=response, text=self.document.label, status_code=404
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_mail_document_view_with_document_access(self):
        self._create_user_mailer()

        self.grant_access(
            permission=permission_mailing_send_document, obj=self.document
        )

        response = self._request_document_send()
        self.assertNotContains(
            response=response, text=self.user_mailer.label, status_code=200
        )
        self.assertContains(
            response=response, text=self.document.label, status_code=200
        )

        self.assertEqual(len(mail.outbox), 0)

    def test_mail_document_view_with_mailer_access(self):
        self._create_user_mailer()

        self.grant_access(
            permission=permission_user_mailer_use, obj=self.user_mailer
        )

        response = self._request_document_send()
        self.assertNotContains(
            response=response, text=self.document.label, status_code=404
        )

        self.assertEqual(len(mail.outbox), 0)

    def test_mail_document_view_with_full_access(self):
        self._create_user_mailer()

        self.grant_access(
            permission=permission_user_mailer_use, obj=self.user_mailer
        )
        self.grant_access(
            permission=permission_mailing_send_document, obj=self.document
        )

        response = self._request_document_send()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(mail.outbox[0].to, [TEST_EMAIL_ADDRESS])

    def test_mail_link_view_recipients_comma(self):
        self._create_user_mailer()

        self.grant_permission(permission=permission_mailing_link)
        self.grant_permission(permission=permission_user_mailer_use)

        self.test_email_address = TEST_RECIPIENTS_MULTIPLE_COMMA
        response = self._request_document_link_send()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(
            mail.outbox[0].to, TEST_RECIPIENTS_MULTIPLE_COMMA_RESULT
        )

    def test_mail_link_view_recipients_mixed(self):
        self._create_user_mailer()

        self.grant_permission(permission=permission_mailing_link)
        self.grant_permission(permission=permission_user_mailer_use)

        self.test_email_address = TEST_RECIPIENTS_MULTIPLE_MIXED
        response = self._request_document_link_send()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(
            mail.outbox[0].to, TEST_RECIPIENTS_MULTIPLE_MIXED_RESULT
        )

    def test_mail_link_view_recipients_semicolon(self):
        self._create_user_mailer()

        self.grant_permission(permission=permission_mailing_link)
        self.grant_permission(permission=permission_user_mailer_use)

        self.test_email_address = TEST_RECIPIENTS_MULTIPLE_SEMICOLON
        response = self._request_document_link_send()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(
            mail.outbox[0].to, TEST_RECIPIENTS_MULTIPLE_SEMICOLON_RESULT
        )

    def test_mail_document_view_recipients_comma(self):
        self._create_user_mailer()

        self.grant_permission(permission=permission_mailing_send_document)
        self.grant_permission(permission=permission_user_mailer_use)

        self.test_email_address = TEST_RECIPIENTS_MULTIPLE_COMMA
        response = self._request_document_send()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(
            mail.outbox[0].to, TEST_RECIPIENTS_MULTIPLE_COMMA_RESULT
        )

    def test_mail_document_view_recipients_mixed(self):
        self._create_user_mailer()

        self.grant_permission(permission=permission_mailing_send_document)
        self.grant_permission(permission=permission_user_mailer_use)

        self.test_email_address = TEST_RECIPIENTS_MULTIPLE_MIXED
        response = self._request_document_send()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(
            mail.outbox[0].to, TEST_RECIPIENTS_MULTIPLE_MIXED_RESULT
        )

    def test_mail_document_view_recipients_semicolon(self):
        self._create_user_mailer()

        self.grant_permission(permission=permission_mailing_send_document)
        self.grant_permission(permission=permission_user_mailer_use)

        self.test_email_address = TEST_RECIPIENTS_MULTIPLE_SEMICOLON
        response = self._request_document_send()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(
            mail.outbox[0].to, TEST_RECIPIENTS_MULTIPLE_SEMICOLON_RESULT
        )

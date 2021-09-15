from __future__ import unicode_literals

import datetime
import logging

from django.utils.timezone import now

from mayan.apps.common.literals import TIME_DELTA_UNIT_DAYS
from mayan.apps.documents.tests import GenericDocumentViewTestCase
from mayan.apps.sources.links import link_upload_version

from ..literals import STATE_CHECKED_OUT, STATE_LABELS
from ..models import DocumentCheckout
from ..permissions import (
    permission_document_check_in, permission_document_check_in_override,
    permission_document_checkout, permission_document_checkout_detail_view
)


class DocumentCheckoutViewTestCase(GenericDocumentViewTestCase):
    create_test_case_superuser = True

    def _checkout_document(self):
        expiration_datetime = now() + datetime.timedelta(days=1)

        DocumentCheckout.objects.checkout_document(
            document=self.document, expiration_datetime=expiration_datetime,
            user=self._test_case_user, block_new_version=True
        )
        self.assertTrue(self.document.is_checked_out())

    def _request_document_check_in_view(self):
        return self.post(
            viewname='checkouts:document_check_in',
            kwargs={'document_id': self.document.pk}
        )

    def test_document_check_in_view_no_permission(self):
        self._checkout_document()

        response = self._request_document_check_in_view()
        self.assertEquals(response.status_code, 404)

        self.assertTrue(self.document.is_checked_out())

    def test_document_check_in_view_with_access(self):
        self._checkout_document()

        self.grant_access(
            obj=self.document, permission=permission_document_check_in
        )
        self.grant_access(
            obj=self.document,
            permission=permission_document_checkout_detail_view
        )
        response = self._request_document_check_in_view()
        self.assertEquals(response.status_code, 302)

        self.assertFalse(self.document.is_checked_out())
        self.assertFalse(
            DocumentCheckout.objects.is_document_checked_out(
                document=self.document
            )
        )

    def _request_document_checkout_view(self):
        return self.post(
            viewname='checkouts:document_checkout',
            kwargs={'document_id': self.document.pk},
            data={
                'expiration_datetime_0': 2,
                'expiration_datetime_1': TIME_DELTA_UNIT_DAYS,
                'block_new_version': True
            }
        )

    def test_checkout_document_view_no_permission(self):
        response = self._request_document_checkout_view()
        self.assertEquals(response.status_code, 404)
        self.assertFalse(self.document.is_checked_out())

    def test_checkout_document_view_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_document_checkout
        )
        self.grant_access(
            obj=self.document,
            permission=permission_document_checkout_detail_view
        )
        response = self._request_document_checkout_view()
        self.assertEquals(response.status_code, 302)

        self.assertTrue(self.document.is_checked_out())

    def _request_checkout_detail_view(self):
        return self.get(
            viewname='checkouts:checkout_info', args=(self.document.pk,),
        )

    def test_checkout_detail_view_no_permission(self):
        self._checkout_document()

        response = self._request_checkout_detail_view()

        self.assertNotContains(
            response, text=STATE_LABELS[STATE_CHECKED_OUT], status_code=403
        )

    def test_checkout_detail_view_with_access(self):
        self._checkout_document()

        self.grant_access(
            obj=self.document,
            permission=permission_document_checkout_detail_view
        )

        response = self._request_checkout_detail_view()

        self.assertContains(response, text=STATE_LABELS[STATE_CHECKED_OUT], status_code=200)

    def test_document_new_version_after_checkout(self):
        """
        Gitlab issue #231
        User shown option to upload new version of a document even though it
        is blocked by checkout - v2.0.0b2

        Expected results:
            - Link to upload version view should not resolve
            - Upload version view should reject request
        """
        self.login_superuser()

        self._checkout_document()

        response = self.post(
            viewname='sources:upload_version',
            kwargs={'document_id': self.document.pk},
            follow=True
        )
        self.assertContains(
            response, text='blocked from uploading',
            status_code=200
        )

        response = self.get(
            viewname='documents:document_version_list',
            kwargs={'document_id': self.document.pk},
            follow=True
        )

        # Needed by the url view resolver
        response.context.current_app = None
        resolved_link = link_upload_version.resolve(context=response.context)

        self.assertEqual(resolved_link, None)

    def test_forcefull_check_in_document_view_no_permission(self):
        # Gitlab issue #237
        # Forcefully checking in a document by a user without adequate
        # permissions throws out an error

        expiration_datetime = now() + datetime.timedelta(days=1)

        # Silence unrelated logging
        logging.getLogger('mayan.apps.navigation.classes').setLevel(
            level=logging.CRITICAL
        )

        DocumentCheckout.objects.checkout_document(
            document=self.document, expiration_datetime=expiration_datetime,
            user=self._test_case_superuser, block_new_version=True
        )

        self.assertTrue(self.document.is_checked_out())

        self.grant_access(
            obj=self.document, permission=permission_document_check_in
        )
        self.grant_access(
            obj=self.document, permission=permission_document_checkout
        )
        response = self.post(
            viewname='checkouts:document_check_in',
            kwargs={'document_id': self.document.pk},
            follow=True
        )
        self.assertContains(
            response, text='Insufficient permissions', status_code=403
        )

        self.assertTrue(self.document.is_checked_out())

    def test_forcefull_check_in_document_view_with_permission(self):
        self._checkout_document()

        self.grant_access(
            obj=self.document, permission=permission_document_check_in
        )
        self.grant_access(
            obj=self.document, permission=permission_document_check_in_override
        )
        self.grant_access(
            obj=self.document, permission=permission_document_checkout_detail_view
        )
        response = self.post(
            viewname='checkouts:document_check_in',
            kwargs={'document_id': self.document.pk},
            follow=True
        )

        self.assertContains(
            response, text='hecked in successfully', status_code=200
        )

        self.assertFalse(self.document.is_checked_out())

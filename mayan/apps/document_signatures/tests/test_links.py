from __future__ import unicode_literals

from django.urls import reverse

from mayan.apps.documents.tests import (
    TEST_DOCUMENT_PATH, GenericDocumentViewTestCase
)

from ..links import (
    link_document_version_signature_delete,
    link_document_version_signature_details
)
from ..permissions import (
    permission_document_version_signature_delete,
    permission_document_version_signature_view
)

from .literals import TEST_SIGNED_DOCUMENT_PATH
from .mixins import SignaturesTestMixin


class DocumentSignatureLinksTestCase(SignaturesTestMixin, GenericDocumentViewTestCase):
    auto_upload_document = False

    def test_document_version_signature_detail_link_no_permission(self):
        self.test_document_path = TEST_SIGNED_DOCUMENT_PATH
        self.test_document = self.upload_document()

        self.add_test_view(
            test_object=self.test_document.latest_version.signatures.first()
        )
        context = self.get_test_view()
        resolved_link = link_document_version_signature_details.resolve(
            context=context
        )

        self.assertEqual(resolved_link, None)

    def test_document_version_signature_detail_link_with_access(self):
        self.test_document_path = TEST_SIGNED_DOCUMENT_PATH
        self.test_document = self.upload_document()

        self.grant_access(
            obj=self.test_document,
            permission=permission_document_version_signature_view
        )

        self.add_test_view(
            test_object=self.test_document.latest_version.signatures.first()
        )
        context = self.get_test_view()
        resolved_link = link_document_version_signature_details.resolve(
            context=context
        )

        self.assertNotEqual(resolved_link, None)
        self.assertEqual(
            resolved_link.url,
            reverse(
                viewname='signatures:document_version_signature_details',
                kwargs={
                    'signature_id': self.test_document.latest_version.signatures.first().pk
                }
            )
        )

    def test_document_version_signature_delete_link_no_permission(self):
        self.test_document_path = TEST_DOCUMENT_PATH
        self.test_document = self.upload_document()
        self._upload_test_signature()

        self.add_test_view(
            test_object=self.test_document.latest_version.signatures.first()
        )
        context = self.get_test_view()
        resolved_link = link_document_version_signature_delete.resolve(
            context=context
        )

        self.assertEqual(resolved_link, None)

    def test_document_version_signature_delete_link_with_access(self):
        self.test_document_path = TEST_DOCUMENT_PATH
        self.test_document = self.upload_document()
        self._upload_test_signature()

        self.grant_access(
            obj=self.test_document,
            permission=permission_document_version_signature_delete
        )

        self.add_test_view(
            test_object=self.test_document.latest_version.signatures.first()
        )
        context = self.get_test_view()
        resolved_link = link_document_version_signature_delete.resolve(
            context=context
        )

        self.assertNotEqual(resolved_link, None)
        self.assertEqual(
            resolved_link.url,
            reverse(
                viewname='signatures:document_version_signature_delete',
                kwargs={
                    'signature_id': self.test_document.latest_version.signatures.first().pk
                }
            )
        )

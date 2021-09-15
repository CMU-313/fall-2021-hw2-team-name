from __future__ import unicode_literals

from django.test import override_settings

from rest_framework import status

from mayan.apps.documents.tests import TEST_HYBRID_DOCUMENT, DocumentTestMixin
from mayan.apps.rest_api.tests import BaseAPITestCase

from ..permissions import permission_content_view, permission_parse_document

from .literals import TEST_DOCUMENT_CONTENT


class DocumentParsingSubmitAPITestCase(DocumentTestMixin, BaseAPITestCase):
    def _request_document_parsing_submit_view(self):
        return self.post(
            viewname='rest_api:document-parsing-submit',
            kwargs={'document_id': self.document.pk}
        )

    def test_submit_document_no_permission(self):
        response = self._request_document_parsing_submit_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertFalse(hasattr(self.document.pages.first(), 'content'))

    #TODO: mock OCR here
    def test_submit_document_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_parse_document
        )
        response = self._request_document_parsing_submit_view()
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        self.assertTrue(hasattr(self.document.pages.first(), 'content'))

    def _request_document_version_parsing_submit_view(self):
        return self.post(
            viewname='rest_api:document_version-parsing-submit',
            kwargs={
                'document_id': self.document.pk,
                'document_version_id': self.document.latest_version.pk
            }
        )

    def test_submit_document_version_no_permission(self):
        response = self._request_document_version_parsing_submit_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertFalse(hasattr(self.document.pages.first(), 'content'))

    def test_submit_document_version_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_parse_document
        )
        response = self._request_document_version_parsing_submit_view()
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        self.assertTrue(hasattr(self.document.pages.first(), 'content'))


@override_settings(DOCUMENT_PARSING_AUTO_PARSING=True)
class DocumentParsingContentAPITestCase(DocumentTestMixin, BaseAPITestCase):
    test_document_filename = TEST_HYBRID_DOCUMENT

    def _request_document_content_view(self):
        return self.get(
            viewname='rest_api:document-parsing-content',
            kwargs={
                'document_id': self.test_document.pk,
            }
        )

    def test_get_document_content_no_permission(self):
        response = self._request_document_content_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_document_content_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_content_view
        )

        response = self._request_document_content_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            TEST_DOCUMENT_CONTENT in response.data['text']
        )

    def _request_document_page_content_view(self):
        latest_version = self.test_document.latest_version

        return self.get(
            viewname='rest_api:document_page-parsing-content',
            kwargs={
                'document_id': self.test_document.pk,
                'document_version_id': latest_version.pk,
                'document_page_id': latest_version.pages.first().pk
            }
        )

    def test_get_document_page_content_no_access(self):
        response = self._request_document_page_content_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_document_page_content_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_content_view
        )
        response = self._request_document_page_content_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            TEST_DOCUMENT_CONTENT in response.data['text']
        )

    def _request_document_version_content_view(self):
        latest_version = self.test_document.latest_version

        return self.get(
            viewname='rest_api:document_version-parsing-content',
            kwargs={
                'document_id': self.test_document.pk,
                'document_version_id': latest_version.pk,
            }
        )

    def test_get_document_version_content_no_permission(self):
        response = self._request_document_version_content_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_document_version_content_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_content_view
        )

        response = self._request_document_version_content_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            TEST_DOCUMENT_CONTENT in response.data['text']
        )

from __future__ import unicode_literals

from django.test import override_settings

from mayan.apps.documents.tests import (
    TEST_HYBRID_DOCUMENT, GenericDocumentViewTestCase
)

from ..permissions import (
    permission_content_view, permission_document_type_parsing_setup,
    permission_parse_document
)
from ..utils import get_document_content_iterator

from .literals import TEST_DOCUMENT_CONTENT


@override_settings(DOCUMENT_PARSING_AUTO_PARSING=True)
class DocumentContentViewsTestCase(GenericDocumentViewTestCase):
    _skip_file_descriptor_test = True

    # Ensure we use a PDF file
    test_document_filename = TEST_HYBRID_DOCUMENT

    def _request_document_content_view(self):
        return self.get(
            viewname='document_parsing:document_content',
            kwargs={'document_id': self.test_document.pk}
        )

    def test_document_content_view_no_permissions(self):
        response = self._request_document_content_view()
        self.assertEqual(response.status_code, 404)

    def test_document_content_view_with_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_content_view
        )

        response = self._request_document_content_view()
        self.assertContains(
            response=response, text=TEST_DOCUMENT_CONTENT, status_code=200
        )

    def _request_document_page_content_view(self):
        return self.get(
            viewname='document_parsing:document_page_content', kwargs={
                'document_page_id': self.test_document.pages.first().pk
            }
        )

    def test_document_page_content_view_no_permissions(self):
        response = self._request_document_page_content_view()
        self.assertEqual(response.status_code, 404)

    def test_document_page_content_view_with_access(self):
        self.grant_access(
            permission=permission_content_view, obj=self.test_document
        )

        response = self._request_document_page_content_view()
        self.assertContains(
            response=response, text=TEST_DOCUMENT_CONTENT, status_code=200
        )

    def _request_document_content_download_view(self):
        return self.get(
            viewname='document_parsing:document_content_download',
            kwargs={'document_id': self.test_document.pk}
        )

    def test_document_parsing_download_view_no_permission(self):
        response = self._request_document_content_download_view()
        self.assertEqual(response.status_code, 404)

    def test_download_view_with_access(self):
        self.expected_content_type = 'application/octet-stream; charset=utf-8'
        self.grant_access(
            permission=permission_content_view, obj=self.test_document
        )

        response = self._request_document_content_download_view()
        self.assertEqual(response.status_code, 200)
        self.assert_download_response(
            content=(
                ''.join(get_document_content_iterator(document=self.test_document))
            ), response=response
        )


class DocumentSubmitViewsTestCase(GenericDocumentViewTestCase):
    _skip_file_descriptor_test = True

    # Ensure we use a PDF file
    test_document_filename = TEST_HYBRID_DOCUMENT

    def _request_document_submit_view(self):
        return self.post(
            viewname='document_parsing:document_submit',
            kwargs={'document_id': self.test_document.pk}
        )

    def test_document_submit_view_no_permission(self):
        response = self._request_document_submit_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(self.test_document.get_content(), '')

    def test_document_submit_view_with_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_parse_document
        )

        response = self._request_document_submit_view()
        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            TEST_DOCUMENT_CONTENT in self.test_document.get_content()
        )

    def _request_multiple_document_submit_view(self):
        return self.post(
            viewname='document_parsing:document_multiple_submit',
            data={
                'id_list': self.test_document.pk,
            }
        )

    def test_multiple_document_submit_view_no_permission(self):
        response = self._request_multiple_document_submit_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(self.test_document.get_content(), '')

    def test_multiple_document_submit_view_with_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_parse_document
        )

        response = self._request_multiple_document_submit_view()
        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            TEST_DOCUMENT_CONTENT in self.test_document.get_content()
        )


class DocumentTypeViewsTestCase(GenericDocumentViewTestCase):
    # Ensure we use a PDF file
    test_document_filename = TEST_HYBRID_DOCUMENT

    def _request_document_type_parsing_settings_view(self):
        return self.get(
            viewname='document_parsing:document_type_parsing_settings',
            kwargs={'document_type_id': self.test_document.document_type.pk}
        )

    def test_document_type_parsing_settings_view_no_permission(self):
        response = self._request_document_type_parsing_settings_view()
        self.assertEqual(response.status_code, 404)

    def test_document_type_parsing_settings_view_with_access(self):
        self.grant_access(
            obj=self.test_document.document_type,
            permission=permission_document_type_parsing_setup
        )
        response = self._request_document_type_parsing_settings_view()

        self.assertEqual(response.status_code, 200)

    def _request_document_type_submit_view(self):
        return self.post(
            viewname='document_parsing:document_type_submit', data={
                'document_type': self.test_document_type.pk,
            }
        )

    def test_document_type_submit_view_no_permission(self):
        response = self._request_document_type_submit_view()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            TEST_DOCUMENT_CONTENT not in self.test_document.get_content()
        )

    def test_document_type_submit_view_with_access(self):
        self.grant_access(
            obj=self.test_document_type, permission=permission_parse_document
        )
        response = self._request_document_type_submit_view()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            TEST_DOCUMENT_CONTENT in self.test_document.get_content()
        )

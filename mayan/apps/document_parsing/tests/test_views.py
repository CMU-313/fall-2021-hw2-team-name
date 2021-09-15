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

    def setUp(self):
        super(DocumentContentViewsTestCase, self).setUp()
        self.login_user()

    def _request_document_content_view(self):
        return self.get(
            'document_parsing:document_content', args=(self.document.pk,)
        )

    def test_document_content_view_no_permissions(self):
        response = self._request_document_content_view()

        self.assertEqual(response.status_code, 403)

    def test_document_content_view_with_access(self):
        self.grant_access(
            permission=permission_content_view, obj=self.document
        )
        response = self._request_document_content_view()

        self.assertContains(
            response=response, text=TEST_DOCUMENT_CONTENT, status_code=200
        )

    def _request_document_page_content_view(self):
        return self.get(
            viewname='document_parsing:document_page_content', args=(
                self.document.pages.first().pk,
            )
        )

    def test_document_page_content_view_no_permissions(self):
        response = self._request_document_page_content_view()

        self.assertEqual(response.status_code, 403)

    def test_document_page_content_view_with_access(self):
        self.grant_access(
            permission=permission_content_view, obj=self.document
        )
        response = self._request_document_page_content_view()

        self.assertContains(
            response=response, text=TEST_DOCUMENT_CONTENT, status_code=200
        )

    def _request_document_content_download_view(self):
        return self.get(
            viewname='document_parsing:document_content_download',
            args=(self.document.pk,)
        )

    def test_document_parsing_download_view_no_permission(self):
        response = self._request_document_content_download_view()
        self.assertEqual(response.status_code, 403)

    def test_download_view_with_access(self):
        self.expected_content_type = 'application/octet-stream; charset=utf-8'
        self.grant_access(
            permission=permission_content_view, obj=self.document
        )
        response = self._request_document_content_download_view()

        self.assertEqual(response.status_code, 200)

        self.assert_download_response(
            response=response, content=(
                ''.join(get_document_content_iterator(document=self.document))
            ),
        )


class DocumentTypeViewsTestCase(GenericDocumentViewTestCase):
    # Ensure we use a PDF file
    test_document_filename = TEST_HYBRID_DOCUMENT

    def setUp(self):
        super(DocumentTypeViewsTestCase, self).setUp()
        self.login_user()

    def _request_document_type_parsing_settings_view(self):
        return self.get(
            viewname='document_parsing:document_type_parsing_settings',
            args=(self.document.document_type.pk,)
        )

    def test_document_type_parsing_settings_view_no_permission(self):
        response = self._request_document_type_parsing_settings_view()
        self.assertEqual(response.status_code, 403)

    def test_document_type_parsing_settings_view_with_access(self):
        self.grant_access(
            permission=permission_document_type_parsing_setup,
            obj=self.document.document_type
        )
        response = self._request_document_type_parsing_settings_view()

        self.assertEqual(response.status_code, 200)

    def _request_document_type_submit_view(self):
        return self.post(
            viewname='document_parsing:document_type_submit', data={
                'document_type': self.document_type.pk,
            }
        )

    def test_document_type_submit_view_no_permission(self):
        response = self._request_document_type_submit_view()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            TEST_DOCUMENT_CONTENT not in self.document.get_content()
        )

    def test_document_type_submit_view_with_access(self):
        self.grant_access(
            obj=self.document_type, permission=permission_parse_document,
        )
        response = self._request_document_type_submit_view()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            TEST_DOCUMENT_CONTENT in self.document.get_content()
        )

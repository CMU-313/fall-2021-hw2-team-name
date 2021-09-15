from __future__ import unicode_literals

from mayan.apps.documents.tests import GenericDocumentViewTestCase

from ..permissions import (
    permission_document_type_ocr_setup, permission_ocr_content_view,
    permission_ocr_document,
)

from .literals import TEST_DOCUMENT_CONTENT


class OCRViewsTestCase(GenericDocumentViewTestCase):
    # PyOCR's leak descriptor in get_available_languages and image_to_string
    # Disable descriptor leak test until fixed in upstream
    _skip_file_descriptor_test = True

    def setUp(self):
        super(OCRViewsTestCase, self).setUp()
        self.login_user()

    def _request_document_content_view(self):
        return self.get(
            viewname='ocr:document_content',
            kwargs={'document_id': self.document.pk}
        )

    def test_document_content_view_no_permissions(self):
        self.document.submit_for_ocr()
        response = self._request_document_content_view()

        self.assertEqual(response.status_code, 404)

    def test_document_content_view_with_access(self):
        self.document.submit_for_ocr()
        self.grant_access(
            permission=permission_ocr_content_view, obj=self.document
        )

        response = self._request_document_content_view()

        self.assertContains(
            response=response, text=TEST_DOCUMENT_CONTENT, status_code=200
        )

    def _request_document_page_content_view(self):
        return self.get(
            viewname='ocr:document_page_content',
            kwargs={'document_page_id': self.document.pages.first().pk}
        )

    def test_document_page_content_view_no_permissions(self):
        self.document.submit_for_ocr()
        response = self._request_document_page_content_view()

        self.assertEqual(response.status_code, 404)

    def test_document_page_content_view_with_access(self):
        self.document.submit_for_ocr()
        self.grant_access(
            permission=permission_ocr_content_view, obj=self.document
        )

        response = self._request_document_page_content_view()

        self.assertContains(
            response=response, text=TEST_DOCUMENT_CONTENT, status_code=200
        )

    def _request_document_submit_view(self):
        return self.post(
            viewname='ocr:document_submit',
            kwargs={'document_id': self.document.pk}
        )

    def test_document_submit_view_no_permission(self):
        self._request_document_submit_view()
        self.assertEqual(self.document.get_ocr_content(), '')

    def test_document_submit_view_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_ocr_document
        )
        self._request_document_submit_view()
        self.assertTrue(
            TEST_DOCUMENT_CONTENT in self.document.get_ocr_content()
        )

    def _request_multiple_document_submit_view(self):
        return self.post(
            viewname='ocr:document_multiple_submit',
            data={
                'id_list': self.document.pk,
            }
        )

    def test_multiple_document_submit_view_no_permission(self):
        self._request_multiple_document_submit_view()
        self.assertEqual(self.document.get_ocr_content(), '')

    def test_multiple_document_submit_view_with_access(self):
        self.grant_access(
            permission=permission_ocr_document, obj=self.document
        )
        self._request_multiple_document_submit_view()
        self.assertTrue(
            TEST_DOCUMENT_CONTENT in self.document.get_ocr_content()
        )

    def _request_document_ocr_download_view(self):
        return self.get(
            viewname='ocr:document_download',
            kwargs={'document_id': self.document.pk}
        )

    def test_document_ocr_download_view_no_permission(self):
        self.document.submit_for_ocr()
        response = self._request_document_ocr_download_view()
        self.assertEqual(response.status_code, 404)

    def test_document_ocr_download_view_with_permission(self):
        self.document.submit_for_ocr()
        self.expected_content_type = 'application/octet-stream; charset=utf-8'

        self.grant_permission(permission=permission_ocr_content_view)
        response = self._request_document_ocr_download_view()

        self.assertEqual(response.status_code, 200)

        self.assert_download_response(
            response=response, content=self.document.get_ocr_content()
        )


class DocumentTypeViewsTestCase(GenericDocumentViewTestCase):
    # PyOCR's leak descriptor in get_available_languages and image_to_string
    # Disable descriptor leak test until fixed in upstream
    _skip_file_descriptor_test = True

    def setUp(self):
        super(DocumentTypeViewsTestCase, self).setUp()
        self.login_user()

    def _request_document_type_ocr_settings_view(self):
        return self.get(
            viewname='ocr:document_type_settings',
            kwargs={'document_type_id': self.document.document_type.pk}
        )

    def test_document_type_ocr_settings_view_no_permission(self):
        response = self._request_document_type_ocr_settings_view()
        self.assertEqual(response.status_code, 404)

    def test_document_type_ocr_settings_view_with_access(self):
        self.grant_access(
            permission=permission_document_type_ocr_setup,
            obj=self.document.document_type
        )
        response = self._request_document_type_ocr_settings_view()

        self.assertEqual(response.status_code, 200)

    def _request_document_type_submit_view(self):
        return self.post(
            viewname='ocr:document_type_submit', data={
                'document_type': self.document_type.pk,
            }
        )

    def test_document_type_submit_view_no_permission(self):
        response = self._request_document_type_submit_view()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            TEST_DOCUMENT_CONTENT not in self.document.get_ocr_content()
        )

    def test_document_type_submit_view_with_access(self):
        self.grant_access(
            obj=self.document_type, permission=permission_ocr_document,
        )
        response = self._request_document_type_submit_view()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            TEST_DOCUMENT_CONTENT in self.document.get_ocr_content()
        )

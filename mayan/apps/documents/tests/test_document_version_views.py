from __future__ import unicode_literals

from django.utils.encoding import force_text

from ..permissions import (
    permission_document_download, permission_document_version_revert,
    permission_document_version_view
)

from .base import GenericDocumentViewTestCase
from .literals import TEST_SMALL_DOCUMENT_PATH, TEST_VERSION_COMMENT


class DocumentVersionTestCase(GenericDocumentViewTestCase):
    def _upload_new_version(self):
        with open(TEST_SMALL_DOCUMENT_PATH, mode='rb') as file_object:
            self.test_document_version = self.document.new_version(
                comment=TEST_VERSION_COMMENT, file_object=file_object
            )

    def _request_document_version_detail_view(self):
        return self.get(
            viewname='documents:document_version_view',
            kwargs={'document_version_id': self.test_document_version.pk}
        )

    def test_document_version_detail_no_permission(self):
        self._upload_new_version()
        response = self._request_document_version_detail_view()
        self.assertEqual(response.status_code, 404)

    def test_document_version_detail_with_access(self):
        self._upload_new_version()
        self.grant_access(
            obj=self.document, permission=permission_document_version_view
        )
        response = self._request_document_version_detail_view()
        self.assertEqual(response.status_code, 200)

    def _request_document_version_download(self, data=None):
        data = data or {}
        return self.get(
            viewname='documents:document_version_download', kwargs={
                'document_version_id': self.document.latest_version.pk,
            }, data=data
        )

    def test_document_version_download_view_no_permission(self):
        response = self._request_document_version_download()
        self.assertEqual(response.status_code, 404)

    def test_document_version_download_view_with_permission(self):
        # Set the expected_content_type for
        # common.tests.mixins.ContentTypeCheckMixin
        self.expected_content_type = '{}; charset=utf-8'.format(
            self.document.latest_version.mimetype
        )

        self.grant_access(
            obj=self.document, permission=permission_document_download
        )
        response = self._request_document_version_download()
        self.assertEqual(response.status_code, 200)

        with self.document.open() as file_object:
            self.assert_download_response(
                response=response, content=file_object.read(),
                basename=force_text(self.document.latest_version),
                mime_type='{}; charset=utf-8'.format(
                    self.document.latest_version.mimetype
                )
            )

    def test_document_version_download_preserve_extension_view_with_permission(self):
        # Set the expected_content_type for
        # common.tests.mixins.ContentTypeCheckMixin
        self.expected_content_type = '{}; charset=utf-8'.format(
            self.document.latest_version.mimetype
        )

        self.grant_access(
            obj=self.document, permission=permission_document_download
        )
        response = self._request_document_version_download(
            data={'preserve_extension': True}
        )

        self.assertEqual(response.status_code, 200)

        with self.document.open() as file_object:
            self.assert_download_response(
                response=response, content=file_object.read(),
                basename=self.document.latest_version.get_rendered_string(
                    preserve_extension=True
                ), mime_type='{}; charset=utf-8'.format(
                    self.document.latest_version.mimetype
                )
            )

    def _request_document_version_list_view(self):
        return self.get(
            viewname='documents:document_version_list',
            kwargs={'document_id': self.document.pk}
        )

    def test_document_version_list_no_permission(self):
        self._upload_new_version()
        response = self._request_document_version_list_view()
        self.assertEqual(response.status_code, 404)

    def test_document_version_list_with_access(self):
        self._upload_new_version()
        self.grant_access(
            obj=self.document, permission=permission_document_version_view
        )
        response = self._request_document_version_list_view()
        self.assertContains(
            response=response, text=TEST_VERSION_COMMENT, status_code=200
        )

    def _request_document_version_revert_view(self):
        return self.post(
            viewname='documents:document_version_revert',
            kwargs={'document_version_id': self.test_document_version_first.pk}
        )

    def test_document_version_revert_no_permission(self):
        self.test_document_version_first = self.document.latest_version
        self._upload_new_version()

        response = self._request_document_version_revert_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.document.versions.count(), 2)

    def test_document_version_revert_with_access(self):
        self.test_document_version_first = self.document.latest_version
        self._upload_new_version()

        self.grant_access(
            obj=self.document, permission=permission_document_version_revert
        )

        response = self._request_document_version_revert_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.document.versions.count(), 1)

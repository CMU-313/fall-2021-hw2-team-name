from __future__ import unicode_literals

from actstream.models import Action
from django_downloadview import assert_download_response

from ..events import event_document_download, event_document_view
from ..permissions import (
    permission_document_download, permission_document_view
)

from .base import GenericDocumentViewTestCase

TEST_DOCUMENT_TYPE_EDITED_LABEL = 'test document type edited label'
TEST_DOCUMENT_TYPE_2_LABEL = 'test document type 2 label'
TEST_TRANSFORMATION_NAME = 'rotate'
TEST_TRANSFORMATION_ARGUMENT = 'degrees: 180'


class DocumentEventsTestCase(GenericDocumentViewTestCase):
    def _request_document_download_view(self):
        return self.get(
            viewname='documents:document_download',
            kwargs={'document_id': self.document.pk}
        )

    def test_document_download_event_no_permissions(self):
        Action.objects.all().delete()

        response = self._request_document_download_view()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(list(Action.objects.any(obj=self.document)), [])

    def test_document_download_event_with_permissions(self):
        Action.objects.all().delete()

        self.grant_access(
            obj=self.document, permission=permission_document_download
        )

        self.expected_content_type = 'image/png; charset=utf-8'

        response = self._request_document_download_view()

        # Download the file to close the file descriptor
        with self.document.open() as file_object:
            assert_download_response(
                self, response, content=file_object.read(),
                mime_type=self.document.file_mimetype
            )

        event = Action.objects.any(obj=self.document).first()

        self.assertEqual(event.verb, event_document_download.id)
        self.assertEqual(event.target, self.document)
        self.assertEqual(event.actor, self._test_case_user)

    def _request_document_preview_view(self):
        return self.get(
            viewname='documents:document_preview',
            kwargs={'document_id': self.document.pk}
        )

    def test_document_view_event_no_permissions(self):
        Action.objects.all().delete()

        response = self._request_document_preview_view()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(list(Action.objects.any(obj=self.document)), [])

    def test_document_view_event_with_access(self):
        Action.objects.all().delete()

        self.grant_access(obj=self.document, permission=permission_document_view)
        response = self._request_document_preview_view()
        self.assertEqual(response.status_code, 200)

        event = Action.objects.any(obj=self.document).first()

        self.assertEqual(event.verb, event_document_view.id)
        self.assertEqual(event.target, self.document)
        self.assertEqual(event.actor, self._test_case_user)

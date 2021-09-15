from __future__ import unicode_literals

from ..models import Document, TrashedDocument
from ..permissions import (
    permission_document_trash, permission_document_view,
    permission_empty_trash, permission_trashed_document_delete,
    permission_trashed_document_restore
)

from .base import GenericDocumentViewTestCase


class TrashedDocumentTestCase(GenericDocumentViewTestCase):
    def _request_document_trash_view(self):
        return self.post(
            viewname='documents:document_trash',
            kwargs={'document_id': self.document.pk}
        )

    def test_document_trash_no_permissions(self):
        response = self._request_document_trash_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TrashedDocument.objects.count(), 0)
        self.assertEqual(Document.objects.count(), 1)

    def test_document_trash_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_document_trash
        )

        response = self._request_document_trash_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TrashedDocument.objects.count(), 1)
        self.assertEqual(Document.objects.count(), 0)

    def _request_trashed_document_restore_view(self):
        return self.post(
            viewname='documents:trashed_document_restore',
            kwargs={'trashed_document_id': self.document.pk}
        )

    def test_trashed_document_restore_view_no_permission(self):
        self.document.delete()
        self.assertEqual(Document.objects.count(), 0)

        response = self._request_trashed_document_restore_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TrashedDocument.objects.count(), 1)
        self.assertEqual(Document.objects.count(), 0)

    def test_trashed_document_restore_view_with_access(self):
        self.document.delete()
        self.assertEqual(Document.objects.count(), 0)

        self.grant_access(
            obj=self.document, permission=permission_trashed_document_restore
        )
        response = self._request_trashed_document_restore_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TrashedDocument.objects.count(), 0)
        self.assertEqual(Document.objects.count(), 1)

    def _request_trashed_document_delete_view(self):
        return self.post(
            viewname='documents:trashed_document_delete',
            kwargs={'trashed_document_id': self.document.pk}
        )

    def test_trashed_document_delete_no_permissions(self):
        self.document.delete()
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(TrashedDocument.objects.count(), 1)

        response = self._request_trashed_document_delete_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(TrashedDocument.objects.count(), 1)

    def test_trashed_document_delete_with_access(self):
        self.document.delete()
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(TrashedDocument.objects.count(), 1)

        self.grant_access(
            obj=self.document, permission=permission_trashed_document_delete
        )

        response = self._request_trashed_document_delete_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TrashedDocument.objects.count(), 0)
        self.assertEqual(Document.objects.count(), 0)

    def _request_trashed_document_list_view(self):
        return self.get(viewname='documents:trashed_document_list')

    def test_trashed_document_list_view_no_permissions(self):
        self.document.delete()

        response = self._request_trashed_document_list_view()
        self.assertNotContains(
            response=response, text=self.document.label, status_code=200
        )

    def test_trashed_document_list_view_with_access(self):
        self.document.delete()

        self.grant_access(
            obj=self.document, permission=permission_document_view
        )
        response = self._request_trashed_document_list_view()

        self.assertContains(
            response=response, text=self.document.label, status_code=200
        )

    def _request_empty_trash_view(self):
        return self.post(viewname='documents:trash_can_empty')

    def test_trash_can_empty_view_no_permission(self):
        self.document.delete()
        self.assertEqual(TrashedDocument.objects.count(), 1)

        response = self._request_empty_trash_view()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(TrashedDocument.objects.count(), 1)

    def test_trash_can_empty_view_with_permission(self):
        self.document.delete()
        self.assertEqual(TrashedDocument.objects.count(), 1)

        self.grant_permission(permission=permission_empty_trash)

        response = self._request_empty_trash_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TrashedDocument.objects.count(), 0)
        self.assertEqual(Document.objects.count(), 0)

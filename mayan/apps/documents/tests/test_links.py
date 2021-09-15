from __future__ import unicode_literals

from django.urls import reverse

from mayan.apps.converter.permissions import (
    permission_transformation_delete, permission_transformation_edit
)

from ..links import (
    link_document_transformations_clear, link_document_transformations_clone,
    link_document_version_revert, link_trashed_document_restore
)
from ..models import TrashedDocument
from ..permissions import (
    permission_trashed_document_restore, permission_document_version_revert
)

from .base import GenericDocumentViewTestCase


class DocumentsLinksTestCase(GenericDocumentViewTestCase):
    use_document_stub = False

    def _resolve_document_version_revert_link(self):
        self.add_test_view(test_object=self.document.versions.first())
        context = self.get_test_view()
        return link_document_version_revert.resolve(context=context)

    def test_document_version_revert_link_no_permission(self):
        self._create_document_version()

        resolved_link = self._resolve_document_version_revert_link()
        self.assertEqual(resolved_link, None)

    def test_document_version_revert_link_with_access(self):
        self._create_document_version()

        self.grant_access(
            obj=self.document, permission=permission_document_version_revert
        )

        resolved_link = self._resolve_document_version_revert_link()
        self.assertNotEqual(resolved_link, None)
        self.assertEqual(
            resolved_link.url,
            reverse(
                viewname='documents:document_version_revert',
                kwargs={'document_version_id': self.document.versions.first().pk}
            )
        )

    def _resolve_document_transformations_clear_link(self):
        self.add_test_view(test_object=self.document)
        context = self.get_test_view()
        return link_document_transformations_clear.resolve(context=context)

    def test_document_transformations_clone_link_no_permission(self):
        resolved_link = self._resolve_document_transformations_clear_link()
        self.assertEqual(resolved_link, None)

    def test_document_transformations_clone_link_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_transformation_delete
        )

        resolved_link = self._resolve_document_transformations_clear_link()
        self.assertNotEqual(resolved_link, None)
        self.assertEqual(
            resolved_link.url,
            reverse(
                viewname='documents:document_transformations_clear',
                kwargs={'document_id': self.document.pk}
            )
        )

    def _resolve_document_transformations_clone_link(self):
        self.add_test_view(test_object=self.document)
        context = self.get_test_view()
        return link_document_transformations_clone.resolve(context=context)

    def test_document_transformations_clone_link_no_permission(self):
        resolved_link = self._resolve_document_transformations_clone_link()
        self.assertEqual(resolved_link, None)

    def test_document_transformations_clone_link_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_transformation_edit
        )

        resolved_link = self._resolve_document_transformations_clone_link()
        self.assertNotEqual(resolved_link, None)
        self.assertEqual(
            resolved_link.url,
            reverse(
                viewname='documents:document_transformations_clone',
                kwargs={'document_id': self.document.pk}
            )
        )


class DeletedDocumentsLinksTestCase(GenericDocumentViewTestCase):
    use_document_stub = True

    def _resolve_trashed_document_restore_link(self):
        self.add_test_view(
            test_object=TrashedDocument.objects.get(pk=self.document.pk)
        )
        context = self.get_test_view()
        return link_trashed_document_restore.resolve(context=context)

    def test_deleted_document_restore_link_no_permission(self):
        self.document.delete()

        resolved_link = self._resolve_trashed_document_restore_link()

        self.assertEqual(resolved_link, None)

    def test_deleted_document_restore_link_with_access(self):
        self.document.delete()

        self.grant_access(
            obj=self.document, permission=permission_trashed_document_restore
        )

        resolved_link = self._resolve_trashed_document_restore_link()

        self.assertNotEqual(resolved_link, None)
        self.assertEqual(
            resolved_link.url,
            reverse(
                viewname='documents:trashed_document_restore',
                kwargs={'trashed_document_id': self.document.pk}
            )
        )

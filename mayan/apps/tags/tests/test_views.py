from __future__ import unicode_literals

from django.utils.encoding import force_text

from mayan.apps.common.tests import GenericViewTestCase
from mayan.apps.documents.tests import GenericDocumentViewTestCase

from ..models import Tag
from ..permissions import (
    permission_tag_attach, permission_tag_create, permission_tag_delete,
    permission_tag_edit, permission_tag_remove, permission_tag_view
)

from .mixins import TagTestMixin, TagViewTestMixin


class TagViewTestCase(TagViewTestMixin, TagTestMixin, GenericViewTestCase):
    def test_tag_create_view_no_permissions(self):
        tag_count = Tag.objects.count()

        response = self._request_tag_create_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(tag_count, Tag.objects.count())

    def test_tag_create_view_with_permissions(self):
        tag_count = Tag.objects.count()

        self.grant_permission(permission=permission_tag_create)
        response = self._request_tag_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(tag_count + 1, Tag.objects.count())

    def test_tag_delete_view_no_permissions(self):
        self._create_test_tag()
        tag_count = Tag.objects.count()

        response = self._request_tag_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(tag_count, Tag.objects.count())

    def test_tag_delete_view_with_access(self):
        self._create_test_tag()
        tag_count = Tag.objects.count()

        self.grant_access(obj=self.test_tag, permission=permission_tag_delete)

        response = self._request_tag_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(tag_count - 1, Tag.objects.count())

    def test_tag_multiple_delete_view_no_permissions(self):
        self._create_test_tag()
        tag_count = Tag.objects.count()

        response = self._request_tag_multiple_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(tag_count, Tag.objects.count())

    def test_tag_multiple_delete_view_with_access(self):
        self._create_test_tag()
        tag_count = Tag.objects.count()

        self.grant_access(obj=self.test_tag, permission=permission_tag_delete)

        response = self._request_tag_multiple_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(tag_count - 1, Tag.objects.count())

    def test_tag_edit_view_no_permissions(self):
        self._create_test_tag()
        tag_label = self.test_tag.label

        response = self._request_tag_edit_view()
        self.assertEqual(response.status_code, 404)

        self.test_tag.refresh_from_db()
        self.assertEqual(tag_label, self.test_tag.label)

    def test_tag_edit_view_with_access(self):
        self._create_test_tag()
        tag_label = self.test_tag.label

        self.grant_access(obj=self.test_tag, permission=permission_tag_edit)

        response = self._request_tag_edit_view()
        self.assertEqual(response.status_code, 302)

        self.test_tag.refresh_from_db()
        self.assertNotEqual(tag_label, self.test_tag.label)


class TagDocumentsViewTestCase(TagViewTestMixin, TagTestMixin, GenericDocumentViewTestCase):
    def test_document_tag_attach_view_no_permission(self):
        self._create_test_tag()

        response = self._request_document_tag_multiple_attach_view()
        self.assertEqual(response.status_code, 404)

        self.assertTrue(self.test_tag not in self.test_document.tags.all())

    def test_document_tag_attach_view_with_document_access(self):
        self._create_test_tag()

        self.grant_access(
            obj=self.test_document, permission=permission_tag_attach
        )
        response = self._request_document_tag_multiple_attach_view()
        self.assertContains(
            response=response, text=force_text(self.test_document),
            status_code=200
        )
        self.assertNotContains(
            response=response, text=force_text(self.test_tag), status_code=200
        )

        self.assertTrue(self.test_tag not in self.test_document.tags.all())

    def test_document_tag_attach_view_with_tag_access(self):
        self._create_test_tag()

        self.grant_access(obj=self.test_tag, permission=permission_tag_attach)
        response = self._request_document_tag_multiple_attach_view()
        self.assertEqual(response.status_code, 404)

        self.assertTrue(self.test_tag not in self.test_document.tags.all())

    def test_document_tag_attach_view_with_full_access(self):
        self._create_test_tag()

        self.grant_access(
            obj=self.test_document, permission=permission_tag_attach
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_attach)
        response = self._request_document_tag_multiple_attach_view()
        self.assertEqual(response.status_code, 302)

        self.assertTrue(self.test_tag in self.test_document.tags.all())

    def test_document_single_tag_attach_view_with_full_access(self):
        """
        Test to make sure only the tag is attached to the selected document
        """
        self._create_test_tag()
        self.test_document_2 = self.upload_document()

        self.grant_access(
            obj=self.test_document, permission=permission_tag_attach
        )
        self.grant_access(
            obj=self.test_document_2, permission=permission_tag_attach
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_attach)
        response = self._request_document_tag_multiple_attach_view()
        self.assertEqual(response.status_code, 302)

        self.assertQuerysetEqual(
            self.test_document.tags.all(), (repr(self.test_tag),)
        )

        self.assertEqual(self.test_document_2.tags.count(), 0)

    def test_document_multiple_tag_attach_view_no_permission(self):
        self._create_test_tag()

        response = self._request_document_multiple_tag_multiple_attach_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.test_document.tags.count(), 0)

    def test_document_multiple_tag_attach_view_with_document_access(self):
        self._create_test_tag()

        self.grant_access(
            obj=self.test_document, permission=permission_tag_attach
        )

        response = self._request_document_multiple_tag_multiple_attach_view()

        self.assertNotContains(
            response=response, text=force_text(self.test_tag), status_code=200
        )

        self.assertEqual(self.test_document.tags.count(), 0)

    def test_document_multiple_tag_attach_view_with_tag_access(self):
        self._create_test_tag()

        self.grant_access(obj=self.test_tag, permission=permission_tag_attach)

        response = self._request_document_multiple_tag_multiple_attach_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.test_document.tags.count(), 0)

    def test_document_multiple_tag_attach_view_with_full_access(self):
        self._create_test_tag()

        self.grant_access(
            obj=self.test_document, permission=permission_tag_attach
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_attach)

        response = self._request_document_multiple_tag_multiple_attach_view()
        self.assertEqual(response.status_code, 302)

        self.assertQuerysetEqual(
            self.test_document.tags.all(), (repr(self.test_tag),)
        )

    def test_document_tag_multiple_remove_view_no_permissions(self):
        self._create_test_tag()

        self.test_document.tags.add(self.test_tag)

        response = self._request_document_tag_multiple_remove_view()
        self.assertEqual(response.status_code, 404)

        self.assertQuerysetEqual(
            self.test_document.tags.all(), (repr(self.test_tag),)
        )

    def test_document_tag_multiple_remove_view_with_document_access(self):
        self._create_test_tag()

        self.test_document.tags.add(self.test_tag)

        self.grant_access(
            obj=self.test_document, permission=permission_tag_remove
        )
        response = self._request_document_tag_multiple_remove_view()
        self.assertNotContains(
            response=response, text=self.test_tag, status_code=200
        )
        self.assertContains(
            response=response, text=self.test_document, status_code=200
        )

        self.assertEqual(self.test_document.tags.count(), 1)

    def test_document_tag_multiple_remove_view_with_tag_access(self):
        self._create_test_tag()

        self.test_document.tags.add(self.test_tag)

        self.grant_access(obj=self.test_tag, permission=permission_tag_remove)

        response = self._request_document_tag_multiple_remove_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(self.test_document.tags.count(), 1)

    def test_document_tag_multiple_remove_view_with_full_access(self):
        self._create_test_tag()

        self.test_document.tags.add(self.test_tag)

        self.grant_access(
            obj=self.test_document, permission=permission_tag_remove
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_remove)

        response = self._request_document_tag_multiple_remove_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(self.test_document.tags.count(), 0)

    def test_document_tags_list_no_permissions(self):
        self._create_test_tag()

        self.test_tag.documents.add(self.test_document)

        response = self._request_document_tag_list_view()
        self.assertNotContains(
            response=response, text=force_text(self.test_tag), status_code=404
        )

    def test_document_tags_list_with_document_access(self):
        self._create_test_tag()

        self.test_tag.documents.add(self.test_document)

        self.grant_access(
            obj=self.test_document, permission=permission_tag_view
        )

        response = self._request_document_tag_list_view()
        self.assertNotContains(
            response=response, text=force_text(self.test_tag), status_code=200
        )

    def test_document_tags_list_with_tag_access(self):
        self._create_test_tag()

        self.test_tag.documents.add(self.test_document)

        self.grant_access(obj=self.test_tag, permission=permission_tag_view)

        response = self._request_document_tag_list_view()
        self.assertNotContains(
            response=response, text=force_text(self.test_tag), status_code=404
        )

    def test_document_tags_list_with_full_access(self):
        self._create_test_tag()

        self.test_tag.documents.add(self.test_document)

        self.grant_access(obj=self.test_tag, permission=permission_tag_view)
        self.grant_access(
            obj=self.test_document, permission=permission_tag_view
        )

        response = self._request_document_tag_list_view()
        self.assertContains(
            response=response, text=force_text(self.test_tag), status_code=200
        )

    def test_document_multiple_tag_remove_view_no_permissions(self):
        self._create_test_tag()

        self.test_document.tags.add(self.test_tag)

        response = self._request_document_multiple_tag_multiple_remove_view()
        self.assertEqual(response.status_code, 404)

        self.assertQuerysetEqual(
            self.test_document.tags.all(), (repr(self.test_tag),)
        )

    def test_document_multiple_tag_remove_view_with_full_access(self):
        self._create_test_tag()

        self.test_document.tags.add(self.test_tag)

        self.grant_access(
            obj=self.test_document, permission=permission_tag_remove
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_remove)

        response = self._request_document_multiple_tag_multiple_remove_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(self.test_document.tags.count(), 0)

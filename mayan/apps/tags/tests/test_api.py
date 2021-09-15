from __future__ import unicode_literals

from django.utils.encoding import force_text

from rest_framework import status

from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests import DocumentTestMixin
from mayan.apps.rest_api.tests import BaseAPITestCase

from ..models import Tag
from ..permissions import (
    permission_tag_attach, permission_tag_create, permission_tag_delete,
    permission_tag_edit, permission_tag_remove, permission_tag_view
)

from .literals import (
    TEST_TAG_COLOR, TEST_TAG_COLOR_EDITED, TEST_TAG_LABEL,
    TEST_TAG_LABEL_EDITED
)
from .mixins import TagAPITestMixin, TagTestMixin


class DocumentTagAPITestCase(TagTestMixin, DocumentTestMixin, BaseAPITestCase):
    auto_upload_document = False

    def _request_api_document_tag_attach_view(self):
        return self.post(
            viewname='rest_api:document-tag-list',
            kwargs={'document_id': self.test_document.pk},
            data={'tag_id': self.test_tag.pk}
        )

    def test_document_tag_attach_view_no_permission(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        response = self._request_api_document_tag_attach_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_tag not in self.test_document.tags.all())

    def test_document_tag_attach_view_with_document_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.grant_access(obj=self.test_document, permission=permission_tag_attach)
        response = self._request_api_document_tag_attach_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_tag not in self.test_document.tags.all())

    def test_document_tag_attach_view_with_tag_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.grant_access(obj=self.test_tag, permission=permission_tag_attach)
        response = self._request_api_document_tag_attach_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_tag not in self.test_document.tags.all())

    def test_document_tag_attach_view_with_full_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.grant_access(
            obj=self.test_document, permission=permission_tag_attach
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_attach)
        response = self._request_api_document_tag_attach_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.test_tag in self.test_document.tags.all())

    def _request_api_document_tag_detail_view(self):
        return self.get(
            viewname='rest_api:document-tag-detail', kwargs={
                'document_id': self.test_document.pk, 'tag_id': self.test_tag.pk
            }
        )

    def test_document_tag_detail_view_no_permission(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        response = self._request_api_document_tag_detail_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_tag_detail_view_with_document_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )
        response = self._request_api_document_tag_detail_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_tag_detail_view_with_tag_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        self.grant_access(obj=self.test_tag, permission=permission_tag_view)
        response = self._request_api_document_tag_detail_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_tag_detail_view_with_full_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        self.grant_access(obj=self.test_tag, permission=permission_tag_view)
        self.grant_access(
            obj=self.test_document, permission=permission_tag_view
        )
        response = self._request_api_document_tag_detail_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['label'], self.test_tag.label)

    def _request_api_document_tag_list_view(self):
        return self.get(
            viewname='rest_api:document-tag-list',
            kwargs={'document_id': self.test_document.pk}
        )

    def test_document_tag_list_view_no_permission(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        response = self._request_api_document_tag_list_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_tag_list_view_with_document_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        self.grant_access(obj=self.test_document, permission=permission_tag_view)
        response = self._request_api_document_tag_list_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_document_tag_list_view_with_tag_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        self.grant_access(obj=self.test_tag, permission=permission_tag_view)
        response = self._request_api_document_tag_list_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_tag_list_view_with_full_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        self.grant_access(obj=self.test_document, permission=permission_tag_view)
        self.grant_access(obj=self.test_tag, permission=permission_tag_view)
        response = self._request_api_document_tag_list_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['label'], self.test_tag.label
        )

    def _request_api_document_tag_remove_view(self):
        return self.delete(
            viewname='rest_api:document-tag-detail', kwargs={
                'document_id': self.test_document.pk, 'tag_id': self.test_tag.pk
            }
        )

    def test_document_tag_remove_view_no_permission(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        response = self._request_api_document_tag_remove_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_tag in self.test_document.tags.all())
        self.assertEqual(Tag.objects.all().count(), 1)

    def test_document_tag_remove_view_with_document_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        self.grant_access(obj=self.test_document, permission=permission_tag_remove)
        response = self._request_api_document_tag_remove_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_tag in self.test_document.tags.all())
        self.assertEqual(Tag.objects.all().count(), 1)

    def test_document_tag_remove_view_with_tag_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        self.grant_access(obj=self.test_tag, permission=permission_tag_remove)
        response = self._request_api_document_tag_remove_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_tag in self.test_document.tags.all())
        self.assertEqual(Tag.objects.all().count(), 1)

    def test_document_tag_remove_view_with_full_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        self.grant_access(
            obj=self.test_document, permission=permission_tag_remove
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_remove)
        response = self._request_api_document_tag_remove_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.test_tag in self.test_document.tags.all())
        self.assertEqual(Tag.objects.all().count(), 1)


class TagAPITestCase(TagAPITestMixin, TagTestMixin, BaseAPITestCase):
    def test_tag_create_view_no_permission(self):
        response = self._request_api_tag_create_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Tag.objects.count(), 0)

    def test_tag_create_view_with_permission(self):
        self.grant_permission(permission=permission_tag_create)
        response = self._request_api_tag_create_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        tag = Tag.objects.first()
        self.assertEqual(response.data['id'], tag.pk)
        self.assertEqual(response.data['label'], TEST_TAG_LABEL)
        self.assertEqual(response.data['color'], TEST_TAG_COLOR)

        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(tag.label, TEST_TAG_LABEL)
        self.assertEqual(tag.color, TEST_TAG_COLOR)

    def test_tag_delete_view_no_permission(self):
        self._create_test_tag()
        response = self._request_api_tag_delete_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_tag in Tag.objects.all())
        self.assertEqual(Tag.objects.all().count(), 1)

    def test_tag_delete_view_with_access(self):
        self._create_test_tag()
        self.grant_access(obj=self.test_tag, permission=permission_tag_delete)
        response = self._request_api_tag_delete_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tag.objects.all().count(), 0)

    def test_tag_edit_patch_view_no_permission(self):
        self._create_test_tag()
        response = self._request_api_tag_edit_patch_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.test_tag.refresh_from_db()
        self.assertEqual(self.test_tag.label, TEST_TAG_LABEL)
        self.assertEqual(self.test_tag.color, TEST_TAG_COLOR)
        self.assertEqual(Tag.objects.all().count(), 1)

    def test_tag_edit_patch_view_with_access(self):
        self._create_test_tag()
        self.grant_access(obj=self.test_tag, permission=permission_tag_edit)
        response = self._request_api_tag_edit_patch_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_tag.refresh_from_db()
        self.assertEqual(self.test_tag.label, TEST_TAG_LABEL_EDITED)
        self.assertEqual(self.test_tag.color, TEST_TAG_COLOR_EDITED)
        self.assertEqual(Tag.objects.all().count(), 1)

    def test_tag_edit_put_view_no_permission(self):
        self._create_test_tag()
        response = self._request_api_tag_edit_put_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.test_tag.refresh_from_db()
        self.assertEqual(self.test_tag.label, TEST_TAG_LABEL)
        self.assertEqual(self.test_tag.color, TEST_TAG_COLOR)
        self.assertEqual(Tag.objects.all().count(), 1)

    def test_tag_edit_put_view_with_access(self):
        self._create_test_tag()
        self.grant_access(obj=self.test_tag, permission=permission_tag_edit)
        response = self._request_api_tag_edit_put_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_tag.refresh_from_db()
        self.assertEqual(self.test_tag.label, TEST_TAG_LABEL_EDITED)
        self.assertEqual(self.test_tag.color, TEST_TAG_COLOR_EDITED)
        self.assertEqual(Tag.objects.all().count(), 1)

    def test_tag_list_view_no_permission(self):
        self._create_test_tag()
        response = self._request_api_tag_list_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_tag_list_view_with_access(self):
        self._create_test_tag()
        self.grant_access(obj=self.test_tag, permission=permission_tag_view)
        response = self._request_api_tag_list_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class TagDocumentAPITestCase(TagTestMixin, DocumentTestMixin, BaseAPITestCase):
    auto_upload_document = False

    def _request_api_tag_document_attach_view(self):
        return self.post(
            viewname='rest_api:tag-document-attach',
            kwargs={'tag_id': self.test_tag.pk},
            data={'document_id': self.test_document.pk}
        )

    def test_tag_document_attach_view_no_permission(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        response = self._request_api_tag_document_attach_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_tag not in self.test_document.tags.all())

    def test_tag_document_attach_view_with_document_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.grant_access(obj=self.test_document, permission=permission_tag_attach)
        response = self._request_api_tag_document_attach_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_tag not in self.test_document.tags.all())

    def test_tag_document_attach_view_with_tag_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.grant_access(obj=self.test_tag, permission=permission_tag_attach)
        response = self._request_api_tag_document_attach_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.test_tag not in self.test_document.tags.all())

    def test_tag_document_attach_view_with_full_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.grant_access(
            obj=self.test_document, permission=permission_tag_attach
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_attach)
        response = self._request_api_tag_document_attach_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.test_tag in self.test_document.tags.all())

    def _request_api_tag_document_list_view(self):
        return self.get(
            viewname='rest_api:tag-document-list',
            kwargs={'tag_id': self.test_tag.pk}
        )

    def test_tag_document_list_view_no_permission(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        response = self._request_api_tag_document_list_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tag_document_list_view_with_tag_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        self.grant_access(obj=self.test_tag, permission=permission_tag_view)
        response = self._request_api_tag_document_list_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_tag_document_list_view_with_document_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )
        response = self._request_api_tag_document_list_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tag_document_list_view_with_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        self.grant_access(obj=self.test_tag, permission=permission_tag_view)
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )
        response = self._request_api_tag_document_list_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['uuid'],
            force_text(self.test_document.uuid)
        )

    def _request_api_tag_document_remove_view(self):
        return self.post(
            viewname='rest_api:tag-document-remove', kwargs={
                'tag_id': self.test_tag.pk
            }, data={'document_id': self.test_document.pk}
        )

    def test_tag_document_remove_view_no_permission(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        response = self._request_api_tag_document_remove_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_tag in self.test_document.tags.all())
        self.assertEqual(Tag.objects.all().count(), 1)

    def test_tag_document_remove_view_with_document_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        self.grant_access(obj=self.test_document, permission=permission_tag_remove)
        response = self._request_api_tag_document_remove_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_tag in self.test_document.tags.all())
        self.assertEqual(Tag.objects.all().count(), 1)

    def test_tag_document_remove_view_with_tag_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        self.grant_access(obj=self.test_tag, permission=permission_tag_remove)
        response = self._request_api_tag_document_remove_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.test_tag in self.test_document.tags.all())
        self.assertEqual(Tag.objects.all().count(), 1)

    def test_tag_document_remove_view_with_full_access(self):
        self._create_test_tag()
        self.test_document = self.upload_document()
        self.test_tag.documents.add(self.test_document)
        self.grant_access(
            obj=self.test_document, permission=permission_tag_remove
        )
        self.grant_access(obj=self.test_tag, permission=permission_tag_remove)
        response = self._request_api_tag_document_remove_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.test_tag not in self.test_document.tags.all())
        self.assertEqual(Tag.objects.all().count(), 1)

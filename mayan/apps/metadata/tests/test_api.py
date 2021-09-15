from __future__ import unicode_literals

import copy

from rest_framework import status

from mayan.apps.documents.permissions import (
    permission_document_type_edit, permission_document_type_view
)
from mayan.apps.documents.tests.mixins import DocumentTestMixin
from mayan.apps.rest_api.tests import BaseAPITestCase

from ..models import MetadataType
from ..permissions import (
    permission_metadata_add, permission_metadata_edit,
    permission_metadata_remove, permission_metadata_view,
    permission_metadata_type_create, permission_metadata_type_delete,
    permission_metadata_type_edit, permission_metadata_type_view
)

from .literals import (
    TEST_METADATA_TYPE_INVALID_LOOKUP, TEST_METADATA_TYPE_LABEL,
    TEST_METADATA_TYPE_LABEL_EDITED, TEST_METADATA_TYPE_NAME,
    TEST_METADATA_TYPE_NAME_EDITED, TEST_METADATA_VALUE,
    TEST_METADATA_VALUE_EDITED
)


class MetadataTypeTestMixin(object):
    def _create_test_metadata_type(self):
        self.test_metadata_type = MetadataType.objects.create(
            label=TEST_METADATA_TYPE_LABEL, name=TEST_METADATA_TYPE_NAME
        )


class MetadataTypeAPITestCase(MetadataTypeTestMixin, BaseAPITestCase):
    def _request_metadata_type_create_api_view(self):
        return self.post(
            viewname='rest_api:metadata_type-list', data={
                'label': TEST_METADATA_TYPE_LABEL,
                'name': TEST_METADATA_TYPE_NAME
            }
        )

    def test_metadata_type_create_api_view_no_permission(self):
        response = self._request_metadata_type_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(MetadataType.objects.count(), 0)

    def test_metadata_type_create_api_view_with_permission(self):
        self.grant_permission(permission=permission_metadata_type_create)

        response = self._request_metadata_type_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(MetadataType.objects.count(), 1)

    def _request_metadata_type_delete_api_view(self):
        return self.delete(
            viewname='rest_api:metadata_type-detail',
            kwargs={'metadata_type_id': self.test_metadata_type.pk}
        )

    def test_metadata_type_delete_api_view_no_permission(self):
        self._create_test_metadata_type()

        response = self._request_metadata_type_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(self.test_metadata_type in MetadataType.objects.all())

    def test_metadata_type_delete_api_view_with_access(self):
        self.expected_content_type = None

        self._create_test_metadata_type()
        self.grant_access(
            obj=self.test_metadata_type, permission=permission_metadata_type_delete
        )

        response = self._request_metadata_type_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertTrue(self.test_metadata_type not in MetadataType.objects.all())

    def _request_metadata_type_detail_api_view(self):
        return self.get(
            viewname='rest_api:metadata_type-detail',
            kwargs={'metadata_type_id': self.test_metadata_type.pk}
        )

    def test_metadata_type_detail_api_view_no_permission(self):
        self._create_test_metadata_type()

        response = self._request_metadata_type_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_metadata_type_detail_api_view_with_access(self):
        self._create_test_metadata_type()
        self.grant_access(
            permission=permission_metadata_type_view, obj=self.test_metadata_type
        )

        response = self._request_metadata_type_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data['label'], self.test_metadata_type.label
        )

    def _request_metadata_type_edit_patch_api_view(self):
        return self.patch(
            viewname='rest_api:metadata_type-detail',
            kwargs={'metadata_type_id': self.test_metadata_type.pk}, data={
                'label': TEST_METADATA_TYPE_LABEL_EDITED,
                'name': TEST_METADATA_TYPE_NAME_EDITED
            }
        )

    def test_metadata_type_patch_api_view_no_permission(self):
        self._create_test_metadata_type()
        test_metadata_type_label = self.test_metadata_type.label
        test_metadata_type_name = self.test_metadata_type.name

        response = self._request_metadata_type_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_metadata_type.refresh_from_db()
        self.assertEqual(self.test_metadata_type.label, test_metadata_type_label)
        self.assertEqual(self.test_metadata_type.name, test_metadata_type_name)

    def test_metadata_type_patch_api_view_with_access(self):
        self._create_test_metadata_type()
        test_metadata_type_label = self.test_metadata_type.label
        test_metadata_type_name = self.test_metadata_type.name
        self.grant_access(
            permission=permission_metadata_type_edit, obj=self.test_metadata_type
        )

        response = self._request_metadata_type_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_metadata_type.refresh_from_db()
        self.assertNotEqual(self.test_metadata_type.label, test_metadata_type_label)
        self.assertNotEqual(self.test_metadata_type.name, test_metadata_type_name)

    def _request_metadata_type_edit_put_api_view(self):
        return self.put(
            viewname='rest_api:metadata_type-detail',
            kwargs={'metadata_type_id': self.test_metadata_type.pk}, data={
                'label': TEST_METADATA_TYPE_LABEL_EDITED,
                'name': TEST_METADATA_TYPE_NAME_EDITED
            }
        )

    def test_metadata_type_edit_put_api_view_no_permission(self):
        self._create_test_metadata_type()
        test_metadata_type_label = self.test_metadata_type.label
        test_metadata_type_name = self.test_metadata_type.name

        response = self._request_metadata_type_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_metadata_type.refresh_from_db()
        self.assertEqual(self.test_metadata_type.label, test_metadata_type_label)
        self.assertEqual(self.test_metadata_type.name, test_metadata_type_name)

    def test_metadata_type_edit_put_api_view_with_access(self):
        self._create_test_metadata_type()
        test_metadata_type_label = self.test_metadata_type.label
        test_metadata_type_name = self.test_metadata_type.name
        self.grant_access(
            permission=permission_metadata_type_edit, obj=self.test_metadata_type
        )
        response = self._request_metadata_type_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_metadata_type.refresh_from_db()
        self.assertNotEqual(self.test_metadata_type.label, test_metadata_type_label)
        self.assertNotEqual(self.test_metadata_type.name, test_metadata_type_name)

    def _request_metadata_type_list_api_view(self):
        return self.get(viewname='rest_api:metadata_type-list')

    def test_metadata_type_list_api_view_no_permission(self):
        self._create_test_metadata_type()
        response = self._request_metadata_type_list_api_view()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_metadata_type_list_api_view_with_access(self):
        self._create_test_metadata_type()
        self.grant_access(
            permission=permission_metadata_type_view, obj=self.test_metadata_type
        )

        response = self._request_metadata_type_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['label'], TEST_METADATA_TYPE_LABEL
        )


class MetadataTypeDocumentTypeRelationTestCase(DocumentTestMixin, MetadataTypeTestMixin, BaseAPITestCase):
    auto_upload_document = False

    def setUp(self):
        super(MetadataTypeDocumentTypeRelationTestCase, self).setUp()
        self._create_test_metadata_type()

    def _create_test_relation(self):
        self.test_object = self.test_metadata_type.document_type_relations.create(
            document_type=self.test_document_type, required=False
        )
        self.relation_required = self.test_object.required

    def _request_metadata_type_document_type_relation_add_api_view(self):
        return self.post(
            viewname='rest_api:metadata_type-document_type_relation-add',
            kwargs={
                'metadata_type_id': self.test_metadata_type.pk,
            },
            data={'document_type_id_list': self.test_document_type.pk}
        )

    def test_metadata_type_document_type_relation_add_api_view_no_permission(self):
        response = self._request_metadata_type_document_type_relation_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertFalse(
            self.test_metadata_type.document_type_relations.filter(
                document_type=self.test_document_type
            ).exists()
        )

    def test_metadata_type_document_type_relation_add_api_view_with_metadata_type_access(self):
        self.grant_access(
            obj=self.test_metadata_type, permission=permission_metadata_type_edit
        )

        response = self._request_metadata_type_document_type_relation_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(
            self.test_metadata_type.document_type_relations.filter(
                document_type=self.test_document_type
            ).exists()
        )

    def test_metadata_type_document_type_relation_add_api_view_with_document_type_access(self):
        self.grant_access(
            obj=self.test_document_type, permission=permission_document_type_edit
        )

        response = self._request_metadata_type_document_type_relation_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertFalse(
            self.test_metadata_type.document_type_relations.filter(
                document_type=self.test_document_type
            ).exists()
        )

    def test_metadata_type_document_type_relation_add_api_view_with_full_access(self):
        self.grant_access(
            obj=self.test_document_type, permission=permission_document_type_edit
        )
        self.grant_access(
            obj=self.test_metadata_type, permission=permission_metadata_type_edit
        )

        response = self._request_metadata_type_document_type_relation_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(
            self.test_metadata_type.document_type_relations.filter(
                document_type=self.test_document_type
            ).exists()
        )

    def _request_document_type_metadata_type_relation_edit_patch_api_view(self):
        return self.patch(
            viewname='rest_api:metadata_type-document_type_relation-detail',
            kwargs={
                'metadata_type_id': self.test_metadata_type.pk,
                'metadata_type_document_type_relation_id': self.test_object.pk,
            }, data={
                'required': True
            }
        )

    def test_document_type_metadata_type_relation_edit_patch_api_view_no_permission(self):
        self._create_test_relation()

        response = self._request_document_type_metadata_type_relation_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_object.refresh_from_db()
        self.assertEqual(self.test_object.required, self.relation_required)

    def test_document_type_metadata_type_relation_edit_patch_api_view_with_metadata_type_permission(self):
        self._create_test_relation()

        self.grant_access(
            obj=self.test_metadata_type, permission=permission_metadata_type_edit
        )

        response = self._request_document_type_metadata_type_relation_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_object.refresh_from_db()
        self.assertEqual(self.test_object.required, self.relation_required)

    def test_document_type_metadata_type_relation_edit_patch_api_view_with_document_type_permission(self):
        self._create_test_relation()

        self.grant_access(
            obj=self.test_document_type, permission=permission_document_type_edit
        )

        response = self._request_document_type_metadata_type_relation_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_object.refresh_from_db()
        self.assertEqual(self.test_object.required, self.relation_required)

    def test_document_type_metadata_type_relation_edit_patch_api_view_with_full_permission(self):
        self._create_test_relation()

        self.grant_access(
            obj=self.test_document_type, permission=permission_document_type_edit
        )
        self.grant_access(
            obj=self.test_metadata_type, permission=permission_metadata_type_edit
        )

        response = self._request_document_type_metadata_type_relation_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_object.refresh_from_db()
        self.assertNotEqual(self.test_object.required, self.relation_required)

    def _request_document_type_metadata_type_relation_edit_put_api_view(self):
        return self.put(
            viewname='rest_api:metadata_type-document_type_relation-detail',
            kwargs={
                'metadata_type_id': self.test_metadata_type.pk,
                'metadata_type_document_type_relation_id': self.test_object.pk,
            }, data={
                'required': True
            }
        )

    def test_document_type_metadata_type_relation_edit_put_api_view_no_permission(self):
        self._create_test_relation()

        response = self._request_document_type_metadata_type_relation_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_object.refresh_from_db()
        self.assertEqual(self.test_object.required, self.relation_required)

    def test_document_type_metadata_type_relation_edit_put_api_view_with_metadata_type_permission(self):
        self._create_test_relation()

        self.grant_access(
            obj=self.test_metadata_type, permission=permission_metadata_type_edit
        )

        response = self._request_document_type_metadata_type_relation_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_object.refresh_from_db()
        self.assertEqual(self.test_object.required, self.relation_required)

    def test_document_type_metadata_type_relation_edit_put_api_view_with_document_type_permission(self):
        self._create_test_relation()

        self.grant_access(
            obj=self.test_document_type, permission=permission_document_type_edit
        )

        response = self._request_document_type_metadata_type_relation_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_object.refresh_from_db()
        self.assertEqual(self.test_object.required, self.relation_required)

    def test_document_type_metadata_type_relation_edit_put_api_view_with_full_permission(self):
        self._create_test_relation()

        self.grant_access(
            obj=self.test_document_type, permission=permission_document_type_edit
        )
        self.grant_access(
            obj=self.test_metadata_type, permission=permission_metadata_type_edit
        )

        response = self._request_document_type_metadata_type_relation_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_object.refresh_from_db()
        self.assertNotEqual(self.test_object.required, self.relation_required)

    def _metadata_type_document_type_relation_list_api_view(self):
        return self.get(
            viewname='rest_api:metadata_type-document_type_relation-list',
            kwargs={'metadata_type_id': self.test_metadata_type.pk}
        )

    def test_metadata_type_document_type_relation_list_api_view_with_no_permission(self):
        self._create_test_relation()

        response = self._metadata_type_document_type_relation_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('results' not in response.json())

    def test_metadata_type_document_type_relation_list_api_view_with_metadata_type_access(self):
        self._create_test_relation()

        self.grant_access(
            obj=self.test_metadata_type, permission=permission_metadata_type_view
        )

        response = self._metadata_type_document_type_relation_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 0)

    def test_metadata_type_document_type_relation_list_api_view_with_document_type_access(self):
        self._create_test_relation()

        self.grant_access(
            obj=self.test_document_type, permission=permission_document_type_view
        )

        response = self._metadata_type_document_type_relation_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('results' not in response.json())

    def test_metadata_type_document_type_relation_list_api_view_with_full_access(self):
        self._create_test_relation()

        self.grant_access(
            obj=self.test_document_type, permission=permission_document_type_view
        )
        self.grant_access(
            obj=self.test_metadata_type, permission=permission_metadata_type_view
        )

        response = self._metadata_type_document_type_relation_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['results'][0]['id'], self.test_object.pk)

    def _request_metadata_type_document_type_relation_remove_api_view(self):
        return self.post(
            viewname='rest_api:metadata_type-document_type_relation-remove',
            kwargs={
                'metadata_type_id': self.test_metadata_type.pk,
            },
            data={'document_type_id_list': self.test_document_type.pk}
        )

    def test_metadata_type_document_type_relation_remove_api_view_no_permission(self):
        self._create_test_relation()

        response = self._request_metadata_type_document_type_relation_remove_api_view()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            self.test_metadata_type.document_type_relations.filter(
                document_type=self.test_document_type
            ).exists()
        )

    def test_metadata_type_document_type_relation_remove_api_view_with_metadata_type_access(self):
        self._create_test_relation()

        self.grant_access(
            obj=self.test_metadata_type, permission=permission_metadata_type_edit
        )

        response = self._request_metadata_type_document_type_relation_remove_api_view()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            self.test_metadata_type.document_type_relations.filter(
                document_type=self.test_document_type
            ).exists()
        )

    def test_metadata_type_document_type_relation_remove_api_view_with_document_type_access(self):
        self._create_test_relation()

        self.grant_access(
            obj=self.test_document_type, permission=permission_document_type_edit
        )

        response = self._request_metadata_type_document_type_relation_remove_api_view()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            self.test_metadata_type.document_type_relations.filter(
                document_type=self.test_document_type
            ).exists()
        )

    def test_metadata_type_document_type_relation_remove_api_view_with_full_access(self):
        self._create_test_relation()

        self.grant_access(
            obj=self.test_document_type, permission=permission_document_type_edit
        )
        self.grant_access(
            obj=self.test_metadata_type, permission=permission_metadata_type_edit
        )

        response = self._request_metadata_type_document_type_relation_remove_api_view()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            self.test_metadata_type.document_type_relations.filter(
                document_type=self.test_document_type
            ).exists()
        )


class DocumentMetadataAPITestCase(DocumentTestMixin, MetadataTypeTestMixin, BaseAPITestCase):
    def setUp(self):
        super(DocumentMetadataAPITestCase, self).setUp()
        self._create_test_metadata_type()
        self._create_test_relation()

    def _create_test_relation(self):
        self.test_object = self.test_metadata_type.document_type_relations.create(
            document_type=self.test_document_type, required=False
        )
        self.relation_required = self.test_object.required

    def _request_document_metadata_create_view(self):
        return self.post(
            viewname='rest_api:document-metadata-list',
            kwargs={'document_id': self.test_document.pk}, data={
                'metadata_type': self.test_metadata_type.pk,
                'value': TEST_METADATA_VALUE
            }
        )

    def test_document_metadata_create_api_view_no_permission(self):
        response = self._request_document_metadata_create_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.document.metadata.count(), 0)

    def test_document_metadata_create_api_view_with_document_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_metadata_add
        )
        response = self._request_document_metadata_create_view()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(self.document.metadata.count(), 0)

    def test_document_metadata_create_api_view_with_metadata_type_access(self):
        self.grant_access(
            obj=self.test_metadata_type, permission=permission_metadata_add
        )

        response = self._request_document_metadata_create_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(self.document.metadata.count(), 0)

    def test_document_metadata_create_api_view_with_full_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_metadata_add
        )
        self.grant_access(
            obj=self.test_metadata_type, permission=permission_metadata_add
        )

        response = self._request_document_metadata_create_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        document_metadata = self.document.metadata.first()
        self.assertEqual(response.data['id'], document_metadata.pk)
        self.assertEqual(document_metadata.metadata_type, self.test_metadata_type)
        self.assertEqual(document_metadata.value, TEST_METADATA_VALUE)

    def _create_test_document_metadata(self):
        self.test_document_metadata = self.test_document.metadata.create(
            metadata_type=self.test_metadata_type, value=TEST_METADATA_VALUE
        )

    def test_document_metadata_create_duplicate_api_view_with_full_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_metadata_add
        )
        self.grant_access(
            obj=self.test_metadata_type, permission=permission_metadata_add
        )
        self._create_test_document_metadata()
        document_metadata_count = self.test_document.metadata.count()

        response = self._request_document_metadata_create_view()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().keys()[0], 'non_field_errors')

        self.assertEqual(
            document_metadata_count, self.test_document.metadata.count()
        )

    def test_document_metadata_create_invalid_lookup_value_api_view_with_full_access(self):
        self.test_metadata_type.lookup = TEST_METADATA_TYPE_INVALID_LOOKUP
        self.test_metadata_type.save()
        self.grant_permission(permission=permission_metadata_add)
        document_metadata_count = self.test_document.metadata.count()

        response = self._request_document_metadata_create_view()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().keys()[0], 'non_field_errors')

        self.assertEqual(
            document_metadata_count, self.test_document.metadata.count()
        )

    def _request_document_metadata_delete_api_view(self):
        return self.delete(
            viewname='rest_api:document-metadata-detail',
            kwargs={
                'document_id': self.test_document.pk,
                'document_metadata_id': self.test_document_metadata.pk
            }
        )

    def test_document_metadata_delete_api_view_no_permission(self):
        self._create_test_document_metadata()

        response = self._request_document_metadata_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(
            self.test_document_metadata in self.document.metadata.all()
        )

    def test_document_metadata_delete_api_view_with_document_access(self):
        self._create_test_document_metadata()
        self.grant_access(
            permission=permission_metadata_remove, obj=self.test_document
        )

        response = self._request_document_metadata_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(
            self.test_document_metadata in self.document.metadata.all()
        )

    def test_document_metadata_delete_api_view_with_metadata_type_access(self):
        self._create_test_document_metadata()
        self.grant_access(
            permission=permission_metadata_remove, obj=self.test_metadata_type
        )

        response = self._request_document_metadata_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(
            self.test_document_metadata in self.document.metadata.all()
        )

    def test_document_metadata_delete_api_view_with_full_access(self):
        self.expected_content_type = None

        self._create_test_document_metadata()
        self.grant_access(
            permission=permission_metadata_remove, obj=self.test_document
        )
        self.grant_access(
            permission=permission_metadata_remove, obj=self.test_metadata_type
        )

        response = self._request_document_metadata_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertTrue(
            self.test_document_metadata not in self.document.metadata.all()
        )

    def _request_document_metadata_edit_patch_api_view(self):
        return self.patch(
            viewname='rest_api:document-metadata-detail',
            kwargs={
                'document_id': self.test_document.pk,
                'document_metadata_id': self.test_document_metadata.pk
            }, data={
                'value': TEST_METADATA_VALUE_EDITED
            }
        )

    def test_document_metadata_edit_patch_api_view_no_permission(self):
        self._create_test_document_metadata()
        test_document_metadata = copy.copy(self.test_document_metadata)

        response = self._request_document_metadata_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_document_metadata.refresh_from_db()
        self.assertTrue(
            test_document_metadata.value == self.test_document_metadata.value
        )

    def test_document_metadata_edit_patch_api_view_with_document_access(self):
        self._create_test_document_metadata()
        self.grant_access(
            permission=permission_metadata_edit, obj=self.test_document
        )
        test_document_metadata = copy.copy(self.test_document_metadata)

        response = self._request_document_metadata_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_document_metadata.refresh_from_db()
        self.assertTrue(
            test_document_metadata.value == self.test_document_metadata.value
        )

    def test_document_metadata_edit_patch_api_view_with_metadata_type_access(self):
        self._create_test_document_metadata()
        self.grant_access(
            permission=permission_metadata_edit, obj=self.test_metadata_type
        )
        test_document_metadata = copy.copy(self.test_document_metadata)

        response = self._request_document_metadata_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_document_metadata.refresh_from_db()
        self.assertTrue(
            test_document_metadata.value == self.test_document_metadata.value
        )

    def test_document_metadata_edit_patch_api_view_with_full_access(self):
        self._create_test_document_metadata()
        self.grant_access(
            permission=permission_metadata_edit, obj=self.test_document
        )
        self.grant_access(
            permission=permission_metadata_edit, obj=self.test_metadata_type
        )
        test_document_metadata = copy.copy(self.test_document_metadata)

        response = self._request_document_metadata_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['value'], TEST_METADATA_VALUE_EDITED
        )

        self.test_document_metadata.refresh_from_db()
        self.assertFalse(
            test_document_metadata.value == self.test_document_metadata.value
        )

    def _request_document_metadata_edit_put_api_view(self):
        return self.put(
            viewname='rest_api:document-metadata-detail',
            kwargs={
                'document_id': self.test_document.pk,
                'document_metadata_id': self.test_document_metadata.pk
            }, data={
                'value': TEST_METADATA_VALUE_EDITED
            }
        )

    def test_document_metadata_edit_put_api_view_no_permission(self):
        self._create_test_document_metadata()
        test_document_metadata = copy.copy(self.test_document_metadata)

        response = self._request_document_metadata_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_document_metadata.refresh_from_db()
        self.assertTrue(
            test_document_metadata.value == self.test_document_metadata.value
        )

    def test_document_metadata_edit_put_api_view_with_document_access(self):
        self._create_test_document_metadata()
        self.grant_access(
            permission=permission_metadata_edit, obj=self.test_document
        )
        test_document_metadata = copy.copy(self.test_document_metadata)

        response = self._request_document_metadata_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_document_metadata.refresh_from_db()
        self.assertTrue(
            test_document_metadata.value == self.test_document_metadata.value
        )

    def test_document_metadata_edit_put_api_view_with_metadata_type_access(self):
        self._create_test_document_metadata()
        self.grant_access(
            permission=permission_metadata_edit, obj=self.test_metadata_type
        )
        test_document_metadata = copy.copy(self.test_document_metadata)

        response = self._request_document_metadata_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_document_metadata.refresh_from_db()
        self.assertTrue(
            test_document_metadata.value == self.test_document_metadata.value
        )

    def test_document_metadata_edit_put_api_view_with_full_access(self):
        self._create_test_document_metadata()
        self.grant_access(
            permission=permission_metadata_edit, obj=self.test_document
        )
        self.grant_access(
            permission=permission_metadata_edit, obj=self.test_metadata_type
        )
        test_document_metadata = copy.copy(self.test_document_metadata)

        response = self._request_document_metadata_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['value'], TEST_METADATA_VALUE_EDITED
        )

        self.test_document_metadata.refresh_from_db()
        self.assertFalse(
            test_document_metadata.value == self.test_document_metadata.value
        )

    def _request_document_metadata_list_api_view(self):
        return self.get(
            viewname='rest_api:document-metadata-list',
            kwargs={'document_id': self.test_document.pk}
        )

    def test_document_metadata_list_api_view_no_permission(self):
        self._create_test_document_metadata()

        response = self._request_document_metadata_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_metadata_list_api_view_document_access(self):
        self._create_test_document_metadata()
        self.grant_access(
            permission=permission_metadata_view, obj=self.test_document
        )

        response = self._request_document_metadata_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 0)

    def test_document_metadata_list_api_view_metadata_type_access(self):
        self._create_test_document_metadata()
        self.grant_access(
            permission=permission_metadata_view, obj=self.test_metadata_type
        )

        response = self._request_document_metadata_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_metadata_list_api_view_with_full_access(self):
        self._create_test_document_metadata()
        self.grant_access(
            permission=permission_metadata_view, obj=self.test_document
        )
        self.grant_access(
            permission=permission_metadata_view, obj=self.test_metadata_type
        )

        response = self._request_document_metadata_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()['results'][0]['document']['id'], self.test_document.pk
        )
        self.assertEqual(
            response.json()['results'][0]['metadata_type']['id'],
            self.test_metadata_type.pk
        )
        self.assertEqual(
            response.json()['results'][0]['value'], self.test_document_metadata.value
        )
        self.assertEqual(
            response.json()['results'][0]['id'], self.test_document_metadata.pk
        )

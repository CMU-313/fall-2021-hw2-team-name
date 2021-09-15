from __future__ import unicode_literals

import logging

from django.utils.encoding import force_text

from mayan.apps.common.tests import GenericViewTestCase
from mayan.apps.documents.models import DocumentType
from mayan.apps.documents.permissions import (
    permission_document_properties_edit, permission_document_type_edit
)
from mayan.apps.documents.tests import (
    DocumentTestMixin, GenericDocumentViewTestCase, TEST_DOCUMENT_TYPE_2_LABEL
)

from ..models import MetadataType
from ..permissions import (
    permission_metadata_add, permission_metadata_remove,
    permission_metadata_edit, permission_metadata_type_create,
    permission_metadata_type_delete, permission_metadata_type_edit,
    permission_metadata_type_view
)

from .literals import (
    TEST_DOCUMENT_METADATA_VALUE_2, TEST_METADATA_TYPE_LABEL,
    TEST_METADATA_TYPE_LABEL_2, TEST_METADATA_TYPE_LABEL_EDITED,
    TEST_METADATA_TYPE_NAME, TEST_METADATA_TYPE_NAME_2,
    TEST_METADATA_TYPE_NAME_EDITED, TEST_METADATA_VALUE_EDITED
)
from .mixins import MetadataTestsMixin


class DocumentMetadataViewTestCase(MetadataTestsMixin, GenericDocumentViewTestCase):
    def setUp(self):
        super(DocumentMetadataViewTestCase, self).setUp()
        self._create_metadata_type()
        self.document_type.metadata_type_relations.create(
            metadata_type=self.metadata_type
        )

    def _request_document_metadata_add_get_view(self):
        return self.get(
            viewname='metadata:document_metadata_add',
            kwargs={'document_id': self.test_document.pk},
        )

    def _request_document_multiple_metadata_add_get_view(self):
        return self.get(
            viewname='metadata:document_multiple_metadata_add',
            data={'id_list': ','.join([force_text(pk) for pk in self.id_list])},
        )

    def _request_document_metadata_add_post_view(self):
        return self.post(
            viewname='metadata:document_metadata_add',
            kwargs={'document_id': self.test_document.pk},
            data={'metadata_type': self.metadata_type.pk}
        )

    def test_document_metadata_add_get_view_no_permission(self):
        response = self._request_document_metadata_add_get_view()
        self.assertNotContains(
            response, text=self.metadata_type.label, status_code=404
        )

    def test_document_metadata_add_get_view_with_full_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_metadata_add
        )
        response = self._request_document_metadata_add_get_view()
        self.assertContains(
            response, text=self.metadata_type.label, status_code=200
        )

    def test_document_individual_metadata_same_type_mixin_with_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_metadata_add
        )

        self._create_document_type_random()
        self.test_document_type.metadata_type_relations.create(
            metadata_type=self.metadata_type
        )
        self._create_document()
        self.grant_access(
            obj=self.test_document, permission=permission_metadata_add
        )

        response = self._request_document_metadata_add_get_view()
        self.assertContains(
            response, text=self.metadata_type.label, status_code=200
        )

    def test_document_single_metadata_same_type_mixin_with_access(self):
        self.id_list = [self.test_document.pk]
        self.grant_access(
            obj=self.test_document, permission=permission_metadata_add
        )

        self._create_document_type_random()
        self.test_document_type.metadata_type_relations.create(
            metadata_type=self.metadata_type
        )
        self._create_document()
        self.grant_access(
            obj=self.test_document, permission=permission_metadata_add
        )

        response = self._request_document_multiple_metadata_add_get_view()
        self.assertContains(
            response, text=self.metadata_type.label, status_code=200
        )

    def test_document_multiple_metadata_same_type_mixin_with_access(self):
        self.id_list = [self.test_document.pk]
        self.grant_access(
            obj=self.test_document, permission=permission_metadata_add
        )

        self._create_document_type_random()
        self.test_document_type.metadata_type_relations.create(
            metadata_type=self.metadata_type
        )
        self._create_document()
        self.id_list.append(self.test_document.pk)
        self.grant_access(
            obj=self.test_document, permission=permission_metadata_add
        )

        response = self._request_document_multiple_metadata_add_get_view()
        self.assertNotContains(
            response, text=self.metadata_type.label, status_code=302
        )

    def test_document_metadata_add_post_view_no_permission(self):
        response = self._request_document_metadata_add_post_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(len(self.document.metadata.all()), 0)

    def test_document_metadata_add_post_view_with_full_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_metadata_add
        )
        response = self._request_document_metadata_add_post_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(self.document.metadata.all()), 1)
        self.assertQuerysetEqual(
            qs=self.document.metadata.values('metadata_type',),
            values=[
                {
                    'metadata_type': self.metadata_type.pk,
                }
            ], transform=dict
        )

    def test_document_metadata_edit_after_document_type_change(self):
        # Gitlab issue #204
        # Problems to add required metadata after changing the document type

        document_type_2 = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_2_LABEL
        )

        metadata_type_2 = MetadataType.objects.create(
            name=TEST_METADATA_TYPE_NAME_2, label=TEST_METADATA_TYPE_LABEL_2
        )

        document_metadata_2 = document_type_2.metadata_type_relations.create(
            metadata_type=metadata_type_2, required=True
        )

        self.grant_access(
            obj=self.document, permission=permission_document_properties_edit
        )
        self.grant_access(
            obj=self.document, permission=permission_metadata_edit
        )
        self.document.set_document_type(document_type=document_type_2)

        response = self.get(
            viewname='metadata:document_metadata_edit',
            kwargs={'document_id': self.document.pk}
        )

        self.assertContains(response, 'Edit', status_code=200)

        response = self.post(
            viewname='metadata:document_metadata_edit',
            kwargs={'document_id': self.document.pk}, data={
                'form-0-id': document_metadata_2.metadata_type.pk,
                'form-0-update': True,
                'form-0-value': TEST_DOCUMENT_METADATA_VALUE_2,
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '',
            }
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.document.metadata.get(metadata_type=metadata_type_2).value,
            TEST_DOCUMENT_METADATA_VALUE_2
        )

    def _request_document_document_metadata_remove_get_view(self):
        return self.get(
            viewname='metadata:document_metadata_remove',
            kwargs={'document_id': self.document.pk}
        )

    def _request_document_document_metadata_remove_post_view(self):
        return self.post(
            viewname='metadata:document_metadata_remove',
            kwargs={'document_id': self.document.pk}, data={
                'form-0-id': self.document_metadata.metadata_type.pk,
                'form-0-update': True,
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '',
            }
        )

    def test_document_metadata_remove_get_view_no_permission(self):
        self.document_metadata = self.document.metadata.create(
            metadata_type=self.metadata_type, value=''
        )

        response = self._request_document_document_metadata_remove_get_view()

        self.assertNotContains(
            response=response, text=self.metadata_type.label, status_code=404
        )

    def test_document_metadata_remove_get_view_with_full_access(self):
        self.document_metadata = self.document.metadata.create(
            metadata_type=self.metadata_type, value=''
        )

        self.grant_access(
            obj=self.document, permission=permission_metadata_remove,
        )

        # Silence unrelated logging
        logging.getLogger('mayan.apps.navigation.classes').setLevel(
            level=logging.CRITICAL
        )

        response = self._request_document_document_metadata_remove_get_view()
        self.assertContains(
            response, text=self.metadata_type.label, status_code=200
        )

    def test_document_metadata_remove_post_view_no_permission(self):
        self.document_metadata = self.document.metadata.create(
            metadata_type=self.metadata_type, value=''
        )

        response = self._request_document_document_metadata_remove_get_view()
        self.assertNotContains(
            response=response, text=self.metadata_type.label, status_code=404
        )

        self.assertEqual(len(self.document.metadata.all()), 1)

    def test_document_metadata_remove_post_view_with_access(self):
        self.document_metadata = self.document.metadata.create(
            metadata_type=self.metadata_type, value=''
        )

        self.grant_access(
            obj=self.test_document, permission=permission_metadata_remove
        )
        response = self._request_document_document_metadata_remove_post_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(self.document.metadata.all()), 0)

    def _request_get_document_multiple_metadata_edit_view(self):
        return self.get(
            viewname='metadata:document_multiple_metadata_edit',
            data={
                'id_list': '{},{}'.format(self.document.pk, self.document_2.pk)
            }
        )

    def _request_post_document_multiple_metadata_edit_view(self):
        return self.post(
            viewname='metadata:document_multiple_metadata_edit', data={
                'id_list': '{},{}'.format(self.document.pk, self.document_2.pk),
                'form-0-id': self.document_metadata.metadata_type.pk,
                'form-0-value': TEST_METADATA_VALUE_EDITED,
                'form-0-update': True,
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '',
            }
        )

    def test_document_multiple_metadata_edit_with_access(self):
        self.document_2 = self.upload_document()

        self.grant_access(
            permission=permission_metadata_edit, obj=self.document
        )
        self.grant_access(
            permission=permission_metadata_edit, obj=self.document_2
        )

        self.document_metadata = self.document.metadata.create(
            metadata_type=self.metadata_type
        )
        self.document_2.metadata.create(metadata_type=self.metadata_type)

        response = self._request_get_document_multiple_metadata_edit_view()

        self.assertContains(
            response, text=self.metadata_type.label, status_code=200
        )

        response = self._request_post_document_multiple_metadata_edit_view()

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.document.metadata.first().value, TEST_METADATA_VALUE_EDITED
        )
        self.assertEqual(
            self.document_2.metadata.first().value, TEST_METADATA_VALUE_EDITED
        )

    def _request_get_document_multiple_metadata_remove_view(self):
        return self.get(
            viewname='metadata:document_multiple_metadata_remove', data={
                'id_list': '{},{}'.format(self.document.pk, self.document_2.pk)
            }
        )

    def _request_post_document_multiple_metadata_remove_view(self):
        return self.post(
            viewname='metadata:document_multiple_metadata_remove', data={
                'id_list': '{},{}'.format(self.document.pk, self.document_2.pk),
                'form-0-id': self.document_metadata.metadata_type.pk,
                'form-0-update': True,
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '',
            }
        )

    def test_document_multiple_metadata_remove_with_access(self):
        self.document_2 = self.upload_document()
        self.grant_access(
            permission=permission_metadata_remove, obj=self.document
        )
        self.grant_access(
            permission=permission_metadata_remove, obj=self.document_2
        )

        self.document_metadata = self.document.metadata.create(
            metadata_type=self.metadata_type
        )
        self.document_2.metadata.create(metadata_type=self.metadata_type)

        response = self._request_get_document_multiple_metadata_remove_view()

        self.assertEquals(response.status_code, 200)

        response = self._request_post_document_multiple_metadata_remove_view()

        self.assertEqual(response.status_code, 302)

        self.assertEqual(self.document.metadata.count(), 0)
        self.assertEqual(self.document_2.metadata.count(), 0)

    def _request_post_document_document_metadata_add_view(self):
        return self.post(
            viewname='metadata:document_multiple_metadata_add', data={
                'id_list': '{},{}'.format(self.document.pk, self.document_2.pk),
                'metadata_type': self.metadata_type.pk
            }
        )

    def test_document_multiple_metadata_add_with_access(self):
        self.document_2 = self.upload_document()

        self.grant_access(
            permission=permission_metadata_add, obj=self.document
        )
        self.grant_access(
            permission=permission_metadata_add, obj=self.document_2
        )

        response = self._request_post_document_document_metadata_add_view()

        self.assertEquals(response.status_code, 302)

        self.assertEqual(self.document.metadata.all().count(), 1)
        self.assertEqual(self.document_2.metadata.all().count(), 1)

    def test_single_document_multiple_metadata_add_view_with_access(self):
        self.grant_access(
            permission=permission_metadata_add, obj=self.document
        )
        metadata_type_2 = MetadataType.objects.create(
            name=TEST_METADATA_TYPE_NAME_2, label=TEST_METADATA_TYPE_LABEL_2
        )

        self.document_type.metadata_type_relations.create(
            metadata_type=metadata_type_2
        )

        self.post(
            viewname='metadata:document_metadata_add',
            kwargs={'document_id': self.document.pk}, data={
                'metadata_type': [self.metadata_type.pk, metadata_type_2.pk],
            }
        )

        document_metadata_types = self.document.metadata.values_list(
            'metadata_type', flat=True
        )
        self.assertTrue(
            self.metadata_type.pk in document_metadata_types and metadata_type_2.pk in document_metadata_types
        )


class MetadataTypeViewViewTestCase(DocumentTestMixin, MetadataTestsMixin, GenericViewTestCase):
    auto_create_document_type = False
    auto_upload_document = False

    def test_metadata_type_create_view_no_permission(self):
        response = self._request_metadata_type_create_view()

        self.assertEqual(response.status_code, 403)

    def test_metadata_type_create_view_with_access(self):
        self.grant_permission(permission=permission_metadata_type_create)
        response = self._request_metadata_type_create_view()

        self.assertEqual(response.status_code, 302)

        self.assertQuerysetEqual(
            qs=MetadataType.objects.values('label', 'name'),
            values=[
                {
                    'label': TEST_METADATA_TYPE_LABEL,
                    'name': TEST_METADATA_TYPE_NAME
                }
            ], transform=dict
        )

    def test_metadata_type_delete_view_no_permission(self):
        self._create_metadata_type()

        response = self._request_metadata_type_delete_view()

        self.assertEqual(response.status_code, 404)
        self.assertQuerysetEqual(
            qs=MetadataType.objects.values('label', 'name'),
            values=[
                {
                    'label': TEST_METADATA_TYPE_LABEL,
                    'name': TEST_METADATA_TYPE_NAME
                }
            ], transform=dict
        )

    def test_metadata_type_delete_view_with_access(self):
        self._create_metadata_type()

        self.grant_access(
            permission=permission_metadata_type_delete,
            obj=self.metadata_type
        )
        response = self._request_metadata_type_delete_view()

        self.assertEqual(response.status_code, 302)

        self.assertEqual(MetadataType.objects.count(), 0)

    def test_metadata_type_edit_view_no_permission(self):
        self._create_metadata_type()

        response = self._request_metadata_type_edit_view()

        self.assertEqual(response.status_code, 404)
        self.assertQuerysetEqual(
            qs=MetadataType.objects.values('label', 'name'),
            values=[
                {
                    'label': TEST_METADATA_TYPE_LABEL,
                    'name': TEST_METADATA_TYPE_NAME
                }
            ], transform=dict
        )

    def test_metadata_type_edit_view_with_access(self):
        self._create_metadata_type()

        self.grant_access(
            permission=permission_metadata_type_edit,
            obj=self.metadata_type
        )
        response = self._request_metadata_type_edit_view()

        self.assertEqual(response.status_code, 302)

        self.assertQuerysetEqual(
            qs=MetadataType.objects.values('label', 'name'),
            values=[
                {
                    'label': TEST_METADATA_TYPE_LABEL_EDITED,
                    'name': TEST_METADATA_TYPE_NAME_EDITED
                }
            ], transform=dict
        )

    def test_metadata_type_list_view_no_permission(self):
        self._create_metadata_type()

        response = self._request_metadata_type_list_view()
        self.assertNotContains(
            response=response, text=self.metadata_type, status_code=200
        )

    def test_metadata_type_list_view_with_access(self):
        self._create_metadata_type()

        self.grant_access(
            permission=permission_metadata_type_view,
            obj=self.metadata_type
        )
        response = self._request_metadata_type_list_view()
        self.assertContains(
            response=response, text=self.metadata_type, status_code=200
        )

    def test_metadata_type_relationship_view_no_permission(self):
        self._create_metadata_type()
        self._create_document_type()
        self.upload_document()

        response = self._request_metadata_type_relationship_edit_view()
        self.assertEqual(response.status_code, 404)

        self.document_type.refresh_from_db()

        self.assertEqual(self.document_type.metadata_type_relations.count(), 0)

    def test_metadata_type_relationship_view_with_document_type_access(self):
        self._create_metadata_type()
        self._create_document_type()
        self.upload_document()

        self.grant_access(
            permission=permission_document_type_edit, obj=self.document_type
        )

        response = self._request_metadata_type_relationship_edit_view()
        self.assertEqual(response.status_code, 404)

        self.document_type.refresh_from_db()

        self.assertEqual(self.document_type.metadata_type_relations.count(), 0)

    def test_metadata_type_relationship_view_with_metadata_type_access(self):
        self._create_metadata_type()
        self._create_document_type()
        self.upload_document()

        self.grant_access(
            permission=permission_metadata_type_edit, obj=self.metadata_type
        )

        response = self._request_metadata_type_relationship_edit_view()

        self.assertEqual(response.status_code, 302)

        self.document_type.refresh_from_db()

        self.assertEqual(self.document_type.metadata_type_relations.count(), 0)

    def test_metadata_type_relationship_view_with_metadata_type_and_document_type_access(self):
        self._create_metadata_type()
        self._create_document_type()
        self.upload_document()

        self.grant_access(
            permission=permission_metadata_type_edit, obj=self.metadata_type
        )
        self.grant_access(
            permission=permission_document_type_edit, obj=self.document_type
        )

        response = self._request_metadata_type_relationship_edit_view()

        self.assertEqual(response.status_code, 302)

        self.document_type.refresh_from_db()

        self.assertQuerysetEqual(
            qs=self.document_type.metadata_type_relations.values(
                'metadata_type', 'required'
            ), values=[
                {
                    'metadata_type': self.metadata_type.pk,
                    'required': True,
                }
            ], transform=dict
        )

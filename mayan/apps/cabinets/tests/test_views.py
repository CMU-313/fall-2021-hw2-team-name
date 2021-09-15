from __future__ import absolute_import, unicode_literals

from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests import GenericDocumentViewTestCase

from ..models import Cabinet
from ..permissions import (
    permission_cabinet_add_document, permission_cabinet_create,
    permission_cabinet_delete, permission_cabinet_edit,
    permission_cabinet_remove_document, permission_cabinet_view
)

from .literals import TEST_CABINET_EDITED_LABEL, TEST_CABINET_LABEL
from .mixins import CabinetTestMixin


class CabinetViewTestCase(CabinetTestMixin, GenericDocumentViewTestCase):
    def setUp(self):
        super(CabinetViewTestCase, self).setUp()
        self.login_user()

    def _request_create_cabinet(self, label):
        return self.post(
            viewname='cabinets:cabinet_create', data={
                'label': TEST_CABINET_LABEL
            }
        )

    def test_cabinet_create_view_no_permission(self):
        response = self._request_create_cabinet(label=TEST_CABINET_LABEL)

        self.assertEquals(response.status_code, 403)
        self.assertEqual(Cabinet.objects.count(), 0)

    def test_cabinet_create_view_with_permission(self):
        self.grant_permission(permission=permission_cabinet_create)

        response = self._request_create_cabinet(label=TEST_CABINET_LABEL)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Cabinet.objects.count(), 1)
        self.assertEqual(Cabinet.objects.first().label, TEST_CABINET_LABEL)

    def test_cabinet_create_duplicate_view_with_permission(self):
        self._create_cabinet()
        self.grant_permission(permission=permission_cabinet_create)
        response = self._request_create_cabinet(label=TEST_CABINET_LABEL)

        # HTTP 200 with error message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cabinet.objects.count(), 1)
        self.assertEqual(Cabinet.objects.first().pk, self.cabinet.pk)

    def _request_delete_cabinet(self):
        return self.post(
            viewname='cabinets:cabinet_delete',
            kwargs={'cabinet_pk': self.cabinet.pk}
        )

    def test_cabinet_delete_view_no_permission(self):
        self._create_cabinet()

        response = self._request_delete_cabinet()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Cabinet.objects.count(), 1)

    def test_cabinet_delete_view_with_access(self):
        self._create_cabinet()
        self.grant_access(obj=self.cabinet, permission=permission_cabinet_delete)

        response = self._request_delete_cabinet()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Cabinet.objects.count(), 0)

    def _request_edit_cabinet(self):
        return self.post(
            viewname='cabinets:cabinet_edit', kwargs={'cabinet_pk': self.cabinet.pk}, data={
                'label': TEST_CABINET_EDITED_LABEL
            }
        )

    def test_cabinet_edit_view_no_permission(self):
        self._create_cabinet()

        response = self._request_edit_cabinet()
        self.assertEqual(response.status_code, 404)
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.label, TEST_CABINET_LABEL)

    def test_cabinet_edit_view_with_access(self):
        self._create_cabinet()

        self.grant_access(obj=self.cabinet, permission=permission_cabinet_edit)

        response = self._request_edit_cabinet()

        self.assertEqual(response.status_code, 302)
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.label, TEST_CABINET_EDITED_LABEL)

    def _request_cabinet_list(self):
        return self.get(viewname='cabinets:cabinet_list')

    def test_cabinet_list_view_no_permission(self):
        self._create_cabinet()
        response = self._request_cabinet_list()
        self.assertNotContains(
            response, text=self.cabinet.label, status_code=200
        )

    def test_cabinet_list_view_with_access(self):
        self._create_cabinet()
        self.grant_access(obj=self.cabinet, permission=permission_cabinet_view)
        response = self._request_cabinet_list()

        self.assertContains(
            response, text=self.cabinet.label, status_code=200
        )


class DocumentViewsTestCase(CabinetTestMixin, GenericDocumentViewTestCase):
    def setUp(self):
        super(DocumentViewsTestCase, self).setUp()
        self.login_user()

    def _add_document_to_cabinet(self):
        return self.post(
            viewname='cabinets:document_cabinet_add', kwargs={
                'document_pk': self.document.pk
            }, data={'cabinets': self.cabinet.pk}
        )

    def test_cabinet_add_document_view_no_permission(self):
        self._create_cabinet()

        response = self._add_document_to_cabinet()

        self.assertContains(
            response, text='Select a valid choice.', status_code=200
        )
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.documents.count(), 0)

    def test_cabinet_add_document_view_with_cabinet_access(self):
        self._create_cabinet()

        self.grant_access(
            obj=self.cabinet, permission=permission_cabinet_add_document
        )
        response = self._add_document_to_cabinet()

        self.assertContains(
            response, text='Select a valid choice.', status_code=404
        )
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.documents.count(), 0)

    def test_cabinet_add_document_view_with_document_access(self):
        self._create_cabinet()

        self.grant_access(
            obj=self.cabinet, permission=permission_cabinet_add_document
        )
        response = self._add_document_to_cabinet()

        self.assertContains(
            response, text='Select a valid choice.', status_code=404
        )
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.documents.count(), 0)

    def test_cabinet_add_document_view_with_full_access(self):
        self._create_cabinet()

        self.grant_access(
            obj=self.cabinet, permission=permission_cabinet_add_document
        )
        self.grant_access(
            obj=self.document, permission=permission_cabinet_add_document
        )

        response = self._add_document_to_cabinet()

        self.cabinet.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.cabinet.documents.count(), 1)
        self.assertQuerysetEqual(
            self.cabinet.documents.all(), (repr(self.document),)
        )

    def _request_add_multiple_documents_to_cabinet(self):
        return self.post(
            viewname='cabinets:document_multiple_cabinet_add', data={
                'id_list': (self.document.pk,), 'cabinets': self.cabinet.pk
            }
        )

    def test_cabinet_add_multiple_documents_view_no_permission(self):
        self._create_cabinet()

        response = self._request_add_multiple_documents_to_cabinet()

        self.assertContains(
            response, text='Select a valid choice', status_code=200
        )
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.documents.count(), 0)

    def test_cabinet_add_multiple_documents_view_with_full_access(self):
        self._create_cabinet()

        self.grant_access(
            obj=self.cabinet, permission=permission_cabinet_add_document
        )
        self.grant_access(
            obj=self.document, permission=permission_cabinet_add_document
        )

        response = self._request_add_multiple_documents_to_cabinet()

        self.assertEqual(response.status_code, 302)
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.documents.count(), 1)
        self.assertQuerysetEqual(
            self.cabinet.documents.all(), (repr(self.document),)
        )

    def _request_remove_document_from_cabinet(self):
        return self.post(
            viewname='cabinets:document_cabinet_remove',
            kwargs={'document_pk': self.document.pk}, data={
                'cabinets': (self.cabinet.pk,),
            }
        )

    def test_cabinet_remove_document_view_no_permission(self):
        self._create_cabinet()

        self.cabinet.documents.add(self.document)

        response = self._request_remove_document_from_cabinet()

        self.assertContains(
            response, text='Select a valid choice', status_code=200
        )

        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.documents.count(), 1)

    def test_cabinet_remove_document_view_with_full_access(self):
        self._create_cabinet()

        self.cabinet.documents.add(self.document)

        self.grant_access(
            obj=self.cabinet, permission=permission_cabinet_remove_document
        )
        self.grant_access(
            obj=self.document, permission=permission_cabinet_remove_document
        )

        response = self._request_remove_document_from_cabinet()

        self.assertEqual(response.status_code, 302)
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.documents.count(), 0)

    def _request_document_cabinet_list(self):
        return self.get(
            viewname='cabinets:document_cabinet_list',
            kwargs={'document_pk': self.document.pk}
        )

    def test_document_cabinet_list_view_no_permission(self):
        self._create_cabinet()
        self.cabinet.documents.add(self.document)
        response = self._request_document_cabinet_list()
        self.assertNotContains(
            response=response, text=self.document.label, status_code=404
        )
        self.assertNotContains(
            response=response, text=self.cabinet.label, status_code=404
        )

    def test_document_cabinet_list_view_with_cabinet_access(self):
        self._create_cabinet()
        self.cabinet.documents.add(self.document)
        self.grant_access(obj=self.cabinet, permission=permission_cabinet_view)
        response = self._request_document_cabinet_list()
        self.assertNotContains(
            response=response, text=self.document.label, status_code=404
        )
        self.assertNotContains(
            response=response, text=self.cabinet.label, status_code=404
        )

    def test_document_cabinet_list_view_with_document_access(self):
        self._create_cabinet()
        self.cabinet.documents.add(self.document)
        self.grant_access(obj=self.document, permission=permission_document_view)
        response = self._request_document_cabinet_list()
        self.assertContains(
            response=response, text=self.document.label, status_code=200
        )
        self.assertNotContains(
            response=response, text=self.cabinet.label, status_code=200
        )

    def test_document_cabinet_list_view_with_full_access(self):
        self._create_cabinet()
        self.cabinet.documents.add(self.document)
        self.grant_access(obj=self.cabinet, permission=permission_cabinet_view)
        self.grant_access(obj=self.document, permission=permission_document_view)
        response = self._request_document_cabinet_list()
        self.assertContains(
            response=response, text=self.document.label, status_code=200
        )
        self.assertContains(
            response=response, text=self.cabinet.label, status_code=200
        )

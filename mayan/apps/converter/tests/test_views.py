from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType

from mayan.apps.documents.tests import GenericDocumentViewTestCase

from ..models import Transformation
from ..permissions import (
    permission_transformation_create, permission_transformation_delete,
    permission_transformation_edit, permission_transformation_view
)

from .literals import (
    TEST_TRANSFORMATION_NAME, TEST_TRANSFORMATION_ARGUMENT,
    TEST_TRANSFORMATION_ARGUMENT_EDITED
)


class TransformationViewsTestCase(GenericDocumentViewTestCase):
    def setUp(self):
        super(TransformationViewsTestCase, self).setUp()
        self.login_user()

    def _transformation_list_view(self):
        return self.get(
            viewname='converter:transformation_list', kwargs={
                'app_label': 'documents', 'model': 'document',
                'object_id': self.document.pk
            }
        )

    def test_transformation_list_view_no_permissions(self):
        response = self._transformation_list_view()

        self.assertEqual(response.status_code, 403)

    def test_transformation_list_view_with_permissions(self):
        self.grant_permission(permission=permission_transformation_view)
        response = self._transformation_list_view()

        self.assertContains(
            response, text=self.document.label, status_code=200
        )

    def _transformation_create_view(self):
        return self.post(
            viewname='converter:transformation_create', kwargs={
                'app_label': 'documents', 'model': 'document',
                'object_id': self.document.pk
            }, data={
                'name': TEST_TRANSFORMATION_NAME,
                'arguments': TEST_TRANSFORMATION_ARGUMENT
            }
        )

    def test_transformation_create_view_no_permissions(self):
        response = self._transformation_create_view()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Transformation.objects.count(), 0)

    def test_transformation_create_view_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_transformation_create
        )
        response = self._transformation_create_view()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Transformation.objects.count(), 1)

    def _create_transformation(self):
        content_type = ContentType.objects.get_for_model(model=self.document)

        self.transformation = Transformation.objects.create(
            content_type=content_type, object_id=self.document.pk,
            name=TEST_TRANSFORMATION_NAME,
            arguments=TEST_TRANSFORMATION_ARGUMENT
        )

    def _transformation_delete_view(self):
        return self.post(
            viewname='converter:transformation_delete', kwargs={
                'pk': self.transformation.pk
            }
        )

    def test_transformation_delete_view_no_permissions(self):
        self._create_transformation()
        response = self._transformation_delete_view()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Transformation.objects.count(), 1)

    def test_transformation_delete_view_with_access(self):
        self._create_transformation()
        self.grant_access(
            obj=self.document, permission=permission_transformation_delete
        )
        response = self._transformation_delete_view()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Transformation.objects.count(), 0)

    def _transformation_edit_view(self):
        return self.post(
            viewname='converter:transformation_edit', kwargs={
                'pk': self.transformation.pk
            }, data={
                'arguments': TEST_TRANSFORMATION_ARGUMENT_EDITED,
                'name': self.transformation.name
            }
        )

    def test_transformation_edit_view_no_permission(self):
        self._create_transformation()
        response = self._transformation_edit_view()
        self.assertEqual(response.status_code, 403)

        self.transformation.refresh_from_db()
        self.assertNotEqual(
            self.transformation.arguments, TEST_TRANSFORMATION_ARGUMENT_EDITED
        )

    def test_transformation_edit_view_with_access(self):
        self._create_transformation()
        self.grant_access(
            obj=self.document, permission=permission_transformation_edit
        )
        response = self._transformation_edit_view()
        self.assertEqual(response.status_code, 302)

        self.transformation.refresh_from_db()
        self.assertEqual(
            self.transformation.arguments, TEST_TRANSFORMATION_ARGUMENT_EDITED
        )

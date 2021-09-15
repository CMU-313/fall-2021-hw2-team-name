from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType

from rest_framework import status

from mayan.apps.documents.tests.mixins import DocumentTestMixin
from mayan.apps.rest_api.tests import BaseAPITestCase

from ..permissions import permission_events_view

from .mixins import EventTypeTestMixin


class EventTypeNamespaceAPITestCase(EventTypeTestMixin, BaseAPITestCase):
    def setUp(self):
        super(EventTypeNamespaceAPITestCase, self).setUp()
        self._create_test_event_type()

    def test_event_type_namespace_list_view(self):
        response = self.get(viewname='rest_api:event_type_namespace-list')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_type_namespace_event_type_list_view(self):
        response = self.get(
            viewname='rest_api:event_type_namespace-event_type-list',
            kwargs={
                'event_type_namespace_name': self.test_event_type_namespace.name
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_type_list_view(self):
        response = self.get(
            viewname='rest_api:event_type-detail',
            kwargs={
                'event_type_namespace_name': self.test_event_type_namespace.name,
                'event_type_id': self.test_event_type.id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DocumentEventAPITestCase(DocumentTestMixin, BaseAPITestCase):
    def setUp(self):
        super(DocumentEventAPITestCase, self).setUp()
        self.test_object = self.test_document

    def _request_object_event_list_api_view(self):
        content_type = ContentType.objects.get_for_model(
            model=self.test_object
        )

        return self.get(
            viewname='rest_api:object-event-list',
            kwargs={
                'app_label': content_type.app_label,
                'model_name': content_type.model,
                'object_id': self.test_object.pk
            }
        )

    def test_object_event_list_view_no_permission(self):
        response = self._request_object_event_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_object_event_list_view_with_access(self):
        self.grant_access(
            obj=self.test_object, permission=permission_events_view
        )
        response = self._request_object_event_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

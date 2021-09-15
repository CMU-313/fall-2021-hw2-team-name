from __future__ import absolute_import, unicode_literals

from rest_framework import status

from mayan.apps.rest_api.tests import BaseAPITestCase

from ..models import AccessControlList
from ..permissions import permission_acl_edit, permission_acl_view

from .mixins import ACLTestMixin


class ACLAPITestCase(ACLTestMixin, BaseAPITestCase):
    def setUp(self):
        super(ACLAPITestCase, self).setUp()
        self._setup_test_object()
        self._create_test_acl()
        self.test_acl.permissions.add(self.test_permission.stored_permission)

    def _request_object_acl_list_api_view(self):
        return self.get(
            viewname='rest_api:object-acl-list',
            kwargs=self.test_content_object_view_kwargs
        )

    def test_object_acl_list_api_view_no_permission(self):
        response = self._request_object_acl_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_object_acl_list_api_view_with_access(self):
        self.grant_access(obj=self.test_object, permission=permission_acl_view)

        response = self._request_object_acl_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['content_type']['app_label'],
            self.test_object_content_type.app_label
        )
        self.assertEqual(
            response.data['results'][0]['role']['label'],
            self.test_acl.role.label
        )

    def _request_acl_delete_api_view(self):
        kwargs = self.test_content_object_view_kwargs.copy()
        kwargs['acl_id'] = self.test_acl.pk

        return self.delete(
            viewname='rest_api:object-acl-detail',
            kwargs=kwargs
        )

    def test_object_acl_delete_api_view_with_access(self):
        self.expected_content_type = None

        self.grant_access(obj=self.test_object, permission=permission_acl_edit)
        response = self._request_acl_delete_api_view()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(self.test_acl not in AccessControlList.objects.all())

    def test_object_acl_delete_api_view_no_permission(self):
        response = self._request_acl_delete_api_view()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_acl in AccessControlList.objects.all())

    def _request_object_acl_detail_api_view(self):
        kwargs = self.test_content_object_view_kwargs.copy()
        kwargs['acl_id'] = self.test_acl.pk

        return self.get(
            viewname='rest_api:object-acl-detail',
            kwargs=kwargs
        )

    def test_object_acl_detail_api_view_with_access(self):
        self.grant_access(obj=self.test_object, permission=permission_acl_view)

        response = self._request_object_acl_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['content_type']['app_label'],
            self.test_object_content_type.app_label
        )
        self.assertEqual(
            response.data['role']['label'], self.test_acl.role.label
        )

    def test_object_acl_detail_api_view_no_permission(self):
        response = self._request_object_acl_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def _request_object_acl_permission_list_api_view(self):
        kwargs = self.test_content_object_view_kwargs.copy()
        kwargs['acl_id'] = self.test_acl.pk

        return self.get(
            viewname='rest_api:object-acl-permission-list',
            kwargs=kwargs
        )

    def test_object_acl_permission_list_api_view_with_access(self):
        self.grant_access(obj=self.test_object, permission=permission_acl_view)

        response = self._request_object_acl_permission_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['pk'],
            self.test_permission.pk
        )

    def test_object_acl_permission_list_api_view_no_permission(self):
        response = self._request_object_acl_permission_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def _request_object_acl_permission_remove_api_view(self):
        kwargs = self.test_content_object_view_kwargs.copy()
        kwargs['acl_id'] = self.test_acl.pk

        return self.post(
            viewname='rest_api:object-acl-permission-remove',
            kwargs=kwargs, data={'permission_id_list': self.test_permission.pk}
        )

    def test_object_acl_permission_remove_api_view_with_access(self):
        self.grant_access(obj=self.test_object, permission=permission_acl_edit)

        response = self._request_object_acl_permission_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.test_permission.stored_permission not in self.test_acl.permissions.all())

    def test_object_acl_permission_remove_api_view_no_permission(self):
        response = self._request_object_acl_permission_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_permission.stored_permission in self.test_acl.permissions.all())

    def _request_object_acl_permission_add_api_view(self):
        kwargs = self.test_content_object_view_kwargs.copy()
        kwargs['acl_id'] = self.test_acl.pk

        return self.post(
            viewname='rest_api:object-acl-permission-add',
            kwargs=kwargs, data={'permission_id_list': self.test_permission.pk}
        )

    def test_object_acl_permission_add_api_view_with_access(self):
        self.test_acl.permissions.clear()
        self.grant_access(obj=self.test_object, permission=permission_acl_edit)

        response = self._request_object_acl_permission_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.test_permission.stored_permission in self.test_acl.permissions.all())

    def test_object_acl_permission_add_api_view_no_permission(self):
        self.test_acl.permissions.clear()

        response = self._request_object_acl_permission_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_permission.stored_permission not in self.test_acl.permissions.all())

    def _request_object_acl_inherited_permission_list_api_view(self):
        kwargs = self.test_content_object_view_kwargs.copy()
        kwargs['acl_id'] = self.test_acl.pk

        return self.get(
            viewname='rest_api:object-acl-permission-inherited-list',
            kwargs=kwargs
        )

    def test_object_acl_inherited_permission_list_api_view_with_access(self):
        self.test_acl.permissions.clear()
        self.test_role.grant(permission=self.test_permission)

        self.grant_access(obj=self.test_object, permission=permission_acl_view)

        response = self._request_object_acl_inherited_permission_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['pk'],
            self.test_permission.pk
        )

    def test_object_acl_inherited_permission_list_api_view_no_permission(self):
        self.test_acl.permissions.clear()
        self.test_role.grant(permission=self.test_permission)

        response = self._request_object_acl_inherited_permission_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

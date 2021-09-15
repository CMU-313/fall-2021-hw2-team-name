from __future__ import unicode_literals

from rest_framework import status

from mayan.apps.rest_api.tests import BaseAPITestCase
from mayan.apps.user_management.permissions import (
    permission_group_edit, permission_group_view
)
from mayan.apps.user_management.tests.mixins import GroupTestMixin

from ..classes import PermissionNamespace
from ..models import Role
from ..permissions import (
    permission_role_create, permission_role_delete, permission_role_edit,
    permission_role_view
)

from .literals import TEST_ROLE_LABEL, TEST_ROLE_LABEL_EDITED
from .mixins import PermissionTestMixin, RoleTestMixin


class PermissionNamespaceAPITestCase(PermissionTestMixin, RoleTestMixin, BaseAPITestCase):
    def _request_permission_namespace_list_api_view(self):
        return self.get(viewname='rest_api:permission_namespace-list')

    def test_permission_namespace_list_api_view(self):
        PermissionNamespace._registry = {}
        self._create_test_permission()

        response = self._request_permission_namespace_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.test_permission_namespace.name, response.json()['results'][0]['name']
        )

    def _request_permission_namespace_permission_list_api_view(self):
        return self.get(
            kwargs={
                'permission_namespace_name': self.test_permission_namespace.name
            }, viewname='rest_api:permission_namespace-permission-list'
        )

    def test_permission_namespace_permission_list_api_view(self):
        self._create_test_permission()

        response = self._request_permission_namespace_permission_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()['results'][0]['pk'], self.test_permission.pk
        )


class RoleAPITestCase(RoleTestMixin, BaseAPITestCase):
    def _request_role_create_api_view(self):
        return self.post(
            viewname='rest_api:role-list', data={
                'label': TEST_ROLE_LABEL
            }
        )

    def test_role_create_api_view_no_permission(self):
        role_count = Role.objects.count()

        response = self._request_role_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(role_count, Role.objects.count())

    def test_role_create_api_view_with_permission(self):
        role_count = Role.objects.count()

        self.grant_permission(permission=permission_role_create)
        response = self._request_role_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(role_count + 1, Role.objects.count())

    def _request_role_delete_api_view(self):
        return self.delete(
            viewname='rest_api:role-detail',
            kwargs={'role_id': self.test_role.pk}
        )

    def test_role_delete_api_view_no_permission(self):
        self._create_test_role()
        role_count = Role.objects.count()

        response = self._request_role_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(role_count, Role.objects.count())

    def test_role_delete_api_view_with_access(self):
        self._create_test_role()
        role_count = Role.objects.count()

        self.grant_access(obj=self.test_role, permission=permission_role_delete)
        response = self._request_role_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(role_count - 1, Role.objects.count())

    def _request_role_edit(self, request_type='patch'):
        return getattr(self, request_type)(
            viewname='rest_api:role-detail', kwargs={'role_id': self.test_role.pk},
            data={
                'label': TEST_ROLE_LABEL_EDITED
            }
        )

    def test_role_edit_patch_api_view_no_permission(self):
        self._create_test_role()
        role_label = self.test_role.label

        response = self._request_role_edit(request_type='patch')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_role.refresh_from_db()
        self.assertEqual(self.test_role.label, role_label)

    def test_role_edit_patch_api_view_with_access(self):
        self._create_test_role()
        role_label = self.test_role.label

        self.grant_access(obj=self.test_role, permission=permission_role_edit)
        response = self._request_role_edit(request_type='patch')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_role.refresh_from_db()
        self.assertNotEqual(self.test_role.label, role_label)

    def test_role_edit_put_api_view_no_permission(self):
        self._create_test_role()
        role_label = self.test_role.label

        response = self._request_role_edit(request_type='put')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_role.refresh_from_db()
        self.assertEqual(self.test_role.label, role_label)

    def test_role_edit_put_api_view_with_access(self):
        self._create_test_role()
        role_label = self.test_role.label

        self.grant_access(obj=self.test_role, permission=permission_role_edit)
        response = self._request_role_edit(request_type='put')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_role.refresh_from_db()
        self.assertNotEqual(self.test_role.label, role_label)

    def _request_role_list_api_view(self):
        return self.get(viewname='rest_api:role-list')

    def test_role_list_api_view_no_permission(self):
        self._create_test_role()

        response = self._request_role_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.test_role.label in response.content)

    def test_role_list_api_view_with_access(self):
        self._create_test_role()

        self.grant_access(obj=self.test_role, permission=permission_role_view)
        response = self._request_role_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(self.test_role.label in response.content)


class RoleGroupAPITestCase(GroupTestMixin, RoleTestMixin, BaseAPITestCase):
    def _request_role_group_list_api_view(self):
        return self.get(
            viewname='rest_api:role-group-list',
            kwargs={'role_id': self.test_role.pk}
        )

    def _request_role_group_add_api_view(self):
        return self.post(
            viewname='rest_api:role-group-add',
            kwargs={'role_id': self.test_role.pk},
            data={'group_id_list': '{}'.format(self.test_group.pk)}
        )

    def _request_role_group_remove_api_view(self):
        return self.post(
            viewname='rest_api:role-group-remove',
            kwargs={'role_id': self.test_role.pk},
            data={'group_id_list': '{}'.format(self.test_group.pk)}
        )

    def _setup_role_group_list(self):
        self._create_test_group()
        self._create_test_role()
        self.test_role.groups.add(self.test_group)

    def test_role_group_list_api_view_no_permission(self):
        self._setup_role_group_list()

        response = self._request_role_group_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_role_group_list_api_view_with_role_access(self):
        self._setup_role_group_list()

        self.grant_access(obj=self.test_role, permission=permission_role_view)
        response = self._request_role_group_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_role_group_list_api_view_with_group_access(self):
        self._setup_role_group_list()

        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_role_group_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_role_group_list_api_view_with_full_access(self):
        self._setup_role_group_list()

        self.grant_access(obj=self.test_role, permission=permission_role_view)
        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_role_group_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def _setup_role_group_add(self):
        self._create_test_group()
        self._create_test_role()

    def test_role_group_add_api_view_no_permission(self):
        self._setup_role_group_add()

        response = self._request_role_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_role.refresh_from_db()
        self.assertTrue(self.test_group not in self.test_role.groups.all())

    def test_role_group_add_api_view_with_role_access(self):
        self._setup_role_group_add()

        self.grant_access(obj=self.test_role, permission=permission_role_edit)
        response = self._request_role_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_role.refresh_from_db()
        self.assertTrue(self.test_group not in self.test_role.groups.all())

    def test_role_group_add_api_view_with_group_access(self):
        self._setup_role_group_add()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_role_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_role.refresh_from_db()
        self.assertTrue(self.test_group not in self.test_role.groups.all())

    def test_role_group_add_api_view_with_full_access(self):
        self._setup_role_group_add()

        self.grant_access(obj=self.test_role, permission=permission_role_edit)
        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_role_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_role.refresh_from_db()
        self.assertTrue(self.test_group in self.test_role.groups.all())

    def _setup_role_group_remove(self):
        self._create_test_group()
        self._create_test_role()
        self.test_role.groups.add(self.test_group)

    def test_role_group_remove_api_view_no_permission(self):
        self._setup_role_group_remove()

        response = self._request_role_group_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_role.refresh_from_db()
        self.assertTrue(self.test_group in self.test_role.groups.all())

    def test_role_group_remove_api_view_with_role_access(self):
        self._setup_role_group_remove()

        self.grant_access(obj=self.test_role, permission=permission_role_edit)
        response = self._request_role_group_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_role.refresh_from_db()
        self.assertTrue(self.test_group in self.test_role.groups.all())

    def test_role_group_remove_api_view_with_group_access(self):
        self._setup_role_group_remove()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_role_group_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_role.refresh_from_db()
        self.assertTrue(self.test_group in self.test_role.groups.all())

    def test_role_group_remove_api_view_with_full_access(self):
        self._setup_role_group_remove()

        self.grant_access(obj=self.test_role, permission=permission_role_edit)
        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_role_group_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_role.refresh_from_db()
        self.assertTrue(self.test_group not in self.test_role.groups.all())


class RolePermissionAPITestCase(PermissionTestMixin, RoleTestMixin, BaseAPITestCase):
    def _request_role_permission_list_api_view(self):
        return self.get(
            viewname='rest_api:role-permission-list',
            kwargs={'role_id': self.test_role.pk}
        )

    def _request_role_permission_add_api_view(self):
        return self.post(
            viewname='rest_api:role-permission-add',
            kwargs={'role_id': self.test_role.pk},
            data={'permission_id_list': '{}'.format(self.test_permission.pk)}
        )

    def _request_role_permission_remove_api_view(self):
        return self.post(
            viewname='rest_api:role-permission-remove',
            kwargs={'role_id': self.test_role.pk},
            data={'permission_id_list': '{}'.format(self.test_permission.pk)}
        )

    def _setup_role_permission_list(self):
        self._create_test_permission()
        self._create_test_role()
        self.test_role.grant(permission=self.test_permission)

    def test_role_permission_list_api_view_no_permission(self):
        self._setup_role_permission_list()

        response = self._request_role_permission_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_role_permission_list_api_view_with_access(self):
        self._setup_role_permission_list()

        self.grant_access(obj=self.test_role, permission=permission_role_view)
        response = self._request_role_permission_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def _setup_role_permission_add(self):
        self._create_test_permission()
        self._create_test_role()

    def test_role_permission_add_api_view_no_permission(self):
        self._setup_role_permission_add()

        response = self._request_role_permission_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_role.refresh_from_db()
        self.assertTrue(self.test_permission not in self.test_role.permissions.all())

    def test_role_permission_add_api_view_with_access(self):
        self._setup_role_permission_add()

        self.grant_access(obj=self.test_role, permission=permission_role_edit)
        response = self._request_role_permission_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_role.refresh_from_db()
        self.assertTrue(
            self.test_permission.stored_permission in self.test_role.permissions.all()
        )

    def _setup_role_permission_remove(self):
        self._create_test_permission()
        self._create_test_role()
        self.test_role.grant(permission=self.test_permission)

    def test_role_permission_remove_api_view_no_permission(self):
        self._setup_role_permission_remove()

        response = self._request_role_permission_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_role.refresh_from_db()
        self.assertTrue(
            self.test_permission.stored_permission in self.test_role.permissions.all()
        )

    def test_role_permission_remove_api_view_with_access(self):
        self._setup_role_permission_remove()

        self.grant_access(obj=self.test_role, permission=permission_role_edit)
        response = self._request_role_permission_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_role.refresh_from_db()
        self.assertTrue(self.test_permission not in self.test_role.permissions.all())

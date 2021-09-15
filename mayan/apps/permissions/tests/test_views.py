from __future__ import unicode_literals

from mayan.apps.common.tests import GenericViewTestCase
from mayan.apps.user_management.permissions import permission_group_edit
from mayan.apps.user_management.tests.mixins import GroupTestMixin

from ..models import Role
from ..permissions import (
    permission_role_create, permission_role_delete, permission_role_edit,
    permission_role_view
)

from .literals import TEST_ROLE_LABEL, TEST_ROLE_LABEL_EDITED
from .mixins import PermissionTestMixin, RoleTestMixin


class RoleViewsTestCase(RoleTestMixin, GenericViewTestCase):
    def _request_create_role_view(self):
        return self.post(
            viewname='permissions:role_create', data={
                'label': TEST_ROLE_LABEL,
            }
        )

    def test_role_creation_view_no_permission(self):
        role_count = Role.objects.count()

        response = self._request_create_role_view()
        self.assertEqual(response.status_code, 403)

        self.assertTrue(role_count == Role.objects.count())

    def test_role_creation_view_with_permission(self):
        role_count = Role.objects.count()

        self.grant_permission(permission=permission_role_create)
        response = self._request_create_role_view()
        self.assertEqual(response.status_code, 302)

        self.assertTrue(role_count + 1 == Role.objects.count())

    def _request_role_delete_view(self):
        return self.post(
            viewname='permissions:role_delete',
            kwargs={'role_id': self.test_role.pk}
        )

    def test_role_delete_view_no_permission(self):
        self._create_test_role()
        role_count = Role.objects.count()

        response = self._request_role_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertTrue(role_count == Role.objects.count())

    def test_role_delete_view_with_access(self):
        self._create_test_role()
        role_count = Role.objects.count()

        self.grant_access(obj=self.test_role, permission=permission_role_delete)
        response = self._request_role_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertTrue(role_count - 1 == Role.objects.count())

    def _request_role_edit_view(self):
        return self.post(
            viewname='permissions:role_edit',
            kwargs={'role_id': self.test_role.pk}, data={
                'label': TEST_ROLE_LABEL_EDITED,
            }
        )

    def test_role_edit_view_no_permission(self):
        self._create_test_role()
        role_label = self.test_role.label

        response = self._request_role_edit_view()
        self.assertEqual(response.status_code, 404)

        self.test_role.refresh_from_db()
        self.assertTrue(role_label == self.test_role.label)

    def test_role_edit_view_with_access(self):
        self._create_test_role()
        role_label = self.test_role.label

        self.grant_access(obj=self.test_role, permission=permission_role_edit)
        response = self._request_role_edit_view()
        self.assertEqual(response.status_code, 302)

        self.test_role.refresh_from_db()
        self.assertTrue(role_label != self.test_role.label)

    def _request_role_list_view(self):
        return self.get(viewname='permissions:role_list')

    def test_role_list_view_no_permission(self):
        self._create_test_role()

        response = self._request_role_list_view()
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response=response, text=self.test_role.label, status_code=200
        )

    def test_role_list_view_with_access(self):
        self._create_test_role()

        self.grant_access(permission=permission_role_view, obj=self.test_role)
        response = self._request_role_list_view()
        self.assertContains(
            response=response, text=self.test_role.label, status_code=200
        )


class RolePermissionViewsTestCase(PermissionTestMixin, RoleTestMixin, GenericViewTestCase):
    def _request_role_permissions_view(self):
        return self.get(
            viewname='permissions:role_permissions',
            kwargs={'role_id': self.test_role.pk}
        )

    def test_role_permissions_view_no_permission(self):
        self._create_test_role()

        response = self._request_role_permissions_view()
        self.assertEqual(response.status_code, 404)

    def test_role_permissions_view_with_access(self):
        self._create_test_role()

        self.grant_access(
            obj=self.test_role, permission=permission_role_edit
        )
        response = self._request_role_permissions_view()
        self.assertEqual(response.status_code, 200)

    def _request_role_permissions_add_view(self):
        return self.post(
            viewname='permissions:role_permissions',
            kwargs={'role_id': self.test_role.pk},
            data={'available-selection': self.test_permission.stored_permission.pk}
        )

    def test_role_permission_add_view_no_permission(self):
        self._create_test_role()
        self._create_test_permission()

        response = self._request_role_permissions_add_view()
        self.assertEqual(response.status_code, 404)

        self.test_role.refresh_from_db()
        self.assertTrue(
            self.test_permission.stored_permission not in self.test_role.permissions.all()
        )

    def test_role_permission_add_view_with_access(self):
        self._create_test_role()
        self._create_test_permission()

        self.grant_access(
            obj=self.test_role, permission=permission_role_edit
        )

        response = self._request_role_permissions_add_view()
        self.assertEqual(response.status_code, 302)

        self.test_role.refresh_from_db()
        self.assertTrue(
            self.test_permission.stored_permission in self.test_role.permissions.all()
        )

    def _request_role_permissions_remove_view(self):
        return self.post(
            viewname='permissions:role_permissions',
            kwargs={'role_id': self.test_role.pk},
            data={'added-selection': self.test_permission.stored_permission.pk}
        )

    def test_role_permission_remove_view_no_permission(self):
        self._create_test_role()
        self._create_test_permission()
        self.test_role.grant(permission=self.test_permission)

        response = self._request_role_permissions_remove_view()
        self.assertEqual(response.status_code, 404)

        self.test_role.refresh_from_db()
        self.assertTrue(
            self.test_permission.stored_permission in self.test_role.permissions.all()
        )

    def test_role_permission_remove_view_with_access(self):
        self._create_test_role()
        self._create_test_permission()
        self.test_role.grant(permission=self.test_permission)

        self.grant_access(
            obj=self.test_role, permission=permission_role_edit
        )

        response = self._request_role_permissions_remove_view()
        self.assertEqual(response.status_code, 302)

        self.test_role.refresh_from_db()
        self.assertTrue(
            self.test_permission.stored_permission not in self.test_role.permissions.all()
        )


class RoleGroupViewsTestCase(GroupTestMixin, RoleTestMixin, GenericViewTestCase):
    def _request_role_groups_view(self):
        return self.get(
            viewname='permissions:role_groups',
            kwargs={'role_id': self.test_role.pk}
        )

    def test_role_groups_view_no_permission(self):
        self._create_test_role()
        self._create_test_group()

        response = self._request_role_groups_view()
        self.assertNotContains(
            response=response, text=self.test_role.label, status_code=404
        )
        self.assertNotContains(
            response=response, text=self.test_group.name, status_code=404
        )

    def test_role_groups_view_with_role_access(self):
        self._create_test_role()
        self._create_test_group()

        self.grant_access(obj=self.test_role, permission=permission_role_edit)
        response = self._request_role_groups_view()
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response=response, text=self.test_role.label, status_code=200
        )
        self.assertNotContains(
            response=response, text=self.test_group.name, status_code=200
        )

    def _request_role_groups_add_view(self):
        return self.post(
            viewname='permissions:role_groups',
            kwargs={'role_id': self.test_role.pk},
            data={'available-selection': self.test_group.pk}
        )

    def test_role_group_add_view_no_permission(self):
        self._create_test_role()
        self._create_test_group()

        response = self._request_role_groups_add_view()
        self.assertEqual(response.status_code, 404)

        self.test_role.refresh_from_db()
        self.assertTrue(
            self.test_group not in self.test_role.groups.all()
        )

    def test_role_group_add_view_with_role_access(self):
        self._create_test_role()
        self._create_test_group()

        self.grant_access(
            obj=self.test_role, permission=permission_role_edit
        )

        response = self._request_role_groups_add_view()
        self.assertContains(
            response=response, text=self.test_role, status_code=200
        )
        self.assertNotContains(
            response=response, text=self.test_group, status_code=200
        )

        self.test_role.refresh_from_db()
        self.assertTrue(
            self.test_group not in self.test_role.groups.all()
        )

    def test_role_group_add_view_with_group_access(self):
        self._create_test_role()
        self._create_test_group()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )

        response = self._request_role_groups_add_view()
        self.assertNotContains(
            response=response, text=self.test_role, status_code=404
        )
        self.assertNotContains(
            response=response, text=self.test_group, status_code=404
        )

        self.test_role.refresh_from_db()
        self.assertTrue(
            self.test_group not in self.test_role.groups.all()
        )

    def test_role_group_add_view_with_full_access(self):
        self._create_test_role()
        self._create_test_group()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        self.grant_access(
            obj=self.test_role, permission=permission_role_edit
        )

        response = self._request_role_groups_add_view()
        self.assertEqual(response.status_code, 302)

        self.test_role.refresh_from_db()
        self.assertTrue(
            self.test_group in self.test_role.groups.all()
        )

    def _request_role_groups_remove_view(self):
        return self.post(
            viewname='permissions:role_groups',
            kwargs={'role_id': self.test_role.pk},
            data={'added-selection': self.test_group.pk}
        )

    def test_role_group_remove_view_no_permission(self):
        self._create_test_role()
        self._create_test_group()
        self.test_role.groups.add(self.test_group)

        response = self._request_role_groups_remove_view()
        self.assertEqual(response.status_code, 404)

        self.test_role.refresh_from_db()
        self.assertTrue(
            self.test_group in self.test_role.groups.all()
        )

    def test_role_group_remove_view_with_role_access(self):
        self._create_test_role()
        self._create_test_group()
        self.test_role.groups.add(self.test_group)

        self.grant_access(
            obj=self.test_role, permission=permission_role_edit
        )

        response = self._request_role_groups_remove_view()
        self.assertContains(
            response=response, text=self.test_role, status_code=200
        )
        self.assertNotContains(
            response=response, text=self.test_group, status_code=200
        )

        self.test_role.refresh_from_db()
        self.assertTrue(
            self.test_group in self.test_role.groups.all()
        )

    def test_role_group_remove_view_with_group_access(self):
        self._create_test_role()
        self._create_test_group()
        self.test_role.groups.add(self.test_group)

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )

        response = self._request_role_groups_remove_view()
        self.assertNotContains(
            response=response, text=self.test_role, status_code=404
        )
        self.assertNotContains(
            response=response, text=self.test_group, status_code=404
        )

        self.test_role.refresh_from_db()
        self.assertTrue(
            self.test_group in self.test_role.groups.all()
        )

    def test_role_group_remove_view_with_full_access(self):
        self._create_test_role()
        self._create_test_group()
        self.test_role.groups.add(self.test_group)

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        self.grant_access(
            obj=self.test_role, permission=permission_role_edit
        )

        response = self._request_role_groups_remove_view()
        self.assertEqual(response.status_code, 302)

        self.test_role.refresh_from_db()
        self.assertTrue(
            self.test_group not in self.test_role.groups.all()
        )


class GroupRoleViewsTestCase(GroupTestMixin, RoleTestMixin, GenericViewTestCase):
    def _request_group_roles_view(self):
        return self.get(
            viewname='permissions:group_roles',
            kwargs={'group_id': self.test_group.pk}
        )

    def test_group_roles_view_no_permission(self):
        self._create_test_group()

        response = self._request_group_roles_view()
        self.assertEqual(response.status_code, 404)

    def test_group_roles_view_with_access(self):
        self._create_test_group()

        self.grant_access(obj=self.test_group, permission=permission_group_edit)
        response = self._request_group_roles_view()
        self.assertEqual(response.status_code, 200)

    def _request_group_roles_add_view(self):
        return self.post(
            viewname='permissions:group_roles',
            kwargs={'group_id': self.test_group.pk},
            data={'available-selection': self.test_role.pk}
        )

    def test_group_role_add_view_no_permission(self):
        self._create_test_group()
        self._create_test_role()

        response = self._request_group_roles_add_view()
        self.assertEqual(response.status_code, 404)

        self.test_group.refresh_from_db()
        self.assertTrue(
            self.test_role not in self.test_group.roles.all()
        )

    def test_group_role_add_view_with_group_access(self):
        self._create_test_group()
        self._create_test_role()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )

        response = self._request_group_roles_add_view()
        self.assertContains(
            response=response, text=self.test_group, status_code=200
        )
        self.assertNotContains(
            response=response, text=self.test_role, status_code=200
        )

        self.test_group.refresh_from_db()
        self.assertTrue(
            self.test_role not in self.test_group.roles.all()
        )

    def test_group_role_add_view_with_role_access(self):
        self._create_test_group()
        self._create_test_role()

        self.grant_access(
            obj=self.test_role, permission=permission_role_edit
        )

        response = self._request_group_roles_add_view()
        self.assertNotContains(
            response=response, text=self.test_group, status_code=404
        )
        self.assertNotContains(
            response=response, text=self.test_role, status_code=404
        )

        self.test_group.refresh_from_db()
        self.assertTrue(
            self.test_role not in self.test_group.roles.all()
        )

    def test_group_role_add_view_with_full_access(self):
        self._create_test_group()
        self._create_test_role()

        self.grant_access(
            obj=self.test_role, permission=permission_role_edit
        )
        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )

        response = self._request_group_roles_add_view()
        self.assertEqual(response.status_code, 302)

        self.test_group.refresh_from_db()
        self.assertTrue(
            self.test_role in self.test_group.roles.all()
        )

    def _request_group_roles_remove_view(self):
        return self.post(
            viewname='permissions:group_roles',
            kwargs={'group_id': self.test_group.pk},
            data={'added-selection': self.test_role.pk}
        )

    def test_group_role_remove_view_no_permission(self):
        self._create_test_group()
        self._create_test_role()
        self.test_group.roles.add(self.test_role)

        response = self._request_group_roles_remove_view()
        self.assertEqual(response.status_code, 404)

        self.test_group.refresh_from_db()
        self.assertTrue(
            self.test_role in self.test_group.roles.all()
        )

    def test_group_role_remove_view_with_group_access(self):
        self._create_test_group()
        self._create_test_role()
        self.test_group.roles.add(self.test_role)

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )

        response = self._request_group_roles_remove_view()
        self.assertContains(
            response=response, text=self.test_group, status_code=200
        )
        self.assertNotContains(
            response=response, text=self.test_role, status_code=200
        )

        self.test_group.refresh_from_db()
        self.assertTrue(
            self.test_role in self.test_group.roles.all()
        )

    def test_group_role_remove_view_with_role_access(self):
        self._create_test_group()
        self._create_test_role()
        self.test_group.roles.add(self.test_role)

        self.grant_access(
            obj=self.test_role, permission=permission_role_edit
        )

        response = self._request_group_roles_remove_view()
        self.assertNotContains(
            response=response, text=self.test_group, status_code=404
        )
        self.assertNotContains(
            response=response, text=self.test_role, status_code=404
        )

        self.test_group.refresh_from_db()
        self.assertTrue(
            self.test_role in self.test_group.roles.all()
        )

    def test_group_role_remove_view_with_full_access(self):
        self._create_test_group()
        self._create_test_role()
        self.test_group.roles.add(self.test_role)

        self.grant_access(
            obj=self.test_role, permission=permission_role_edit
        )
        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )

        response = self._request_group_roles_remove_view()
        self.assertEqual(response.status_code, 302)

        self.test_group.refresh_from_db()
        self.assertTrue(
            self.test_role not in self.test_group.roles.all()
        )

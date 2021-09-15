from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied

from mayan.apps.common.tests import BaseTestCase

from ..classes import Permission, PermissionNamespace
from ..models import StoredPermission
from ..permissions import permission_role_view

from .literals import (
    TEST_INVALID_PERMISSION_NAME, TEST_INVALID_PERMISSION_NAMESPACE_NAME,
    TEST_PERMISSION_LABEL, TEST_PERMISSION_NAME,
    TEST_PERMISSION_NAMESPACE_LABEL, TEST_PERMISSION_NAMESPACE_NAME
)


class PermissionTestCase(BaseTestCase):
    def test_no_permissions(self):
        with self.assertRaises(PermissionDenied):
            Permission.check_user_permission(
                permission=permission_role_view, user=self._test_case_user
            )

    def test_with_permissions(self):
        self._test_case_group.user_set.add(self._test_case_user)
        self._test_case_role.permissions.add(permission_role_view.stored_permission)
        self._test_case_role.groups.add(self._test_case_group)

        try:
            Permission.check_user_permission(
                permission=permission_role_view, user=self._test_case_user
            )
        except PermissionDenied:
            self.fail('PermissionDenied exception was not expected.')


class StoredPermissionManagerTestCase(BaseTestCase):
    create_test_case_superuser = False
    create_test_case_user = False

    def test_purge_obsolete_with_invalid(self):
        StoredPermission.objects.create(
            namespace=TEST_INVALID_PERMISSION_NAMESPACE_NAME,
            name=TEST_INVALID_PERMISSION_NAME
        )

        StoredPermission.objects.purge_obsolete()

        self.assertEqual(StoredPermission.objects.count(), 0)

    def test_purge_obsolete_with_valid(self):
        test_permission_namespace = PermissionNamespace(
            label=TEST_PERMISSION_NAMESPACE_LABEL,
            name=TEST_PERMISSION_NAMESPACE_NAME
        )
        test_permission = test_permission_namespace.add_permission(
            label=TEST_PERMISSION_LABEL, name=TEST_PERMISSION_NAME
        )
        test_permission.stored_permission

        StoredPermission.objects.purge_obsolete()

        self.assertEqual(StoredPermission.objects.count(), 1)

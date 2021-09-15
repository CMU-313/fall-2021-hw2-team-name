from __future__ import unicode_literals

from ..classes import PermissionNamespace
from ..models import Role

from .literals import (
    TEST_CASE_ROLE_LABEL, TEST_PERMISSION_LABEL, TEST_PERMISSION_LABEL_2,
    TEST_PERMISSION_NAME, TEST_PERMISSION_NAME_2, TEST_PERMISSION_NAMESPACE_LABEL,
    TEST_PERMISSION_NAMESPACE_LABEL_2, TEST_PERMISSION_NAMESPACE_NAME,
    TEST_PERMISSION_NAMESPACE_NAME_2, TEST_ROLE_LABEL
)


class PermissionTestMixin(object):
    def _create_test_permission(self):
        self.test_permission_namespace = PermissionNamespace(
            label=TEST_PERMISSION_NAMESPACE_LABEL,
            name=TEST_PERMISSION_NAMESPACE_NAME
        )
        self.test_permission = self.test_permission_namespace.add_permission(
            label=TEST_PERMISSION_LABEL,
            name=TEST_PERMISSION_NAME
        )

    def _create_test_permission_2(self):
        self.test_permission_namespace_2 = PermissionNamespace(
            label=TEST_PERMISSION_NAMESPACE_LABEL_2,
            name=TEST_PERMISSION_NAMESPACE_NAME_2
        )
        self.test_permission_2 = self.test_permission_namespace_2.add_permission(
            label=TEST_PERMISSION_LABEL_2,
            name=TEST_PERMISSION_NAME_2
        )


class RoleTestCaseMixin(object):
    def setUp(self):
        super(RoleTestCaseMixin, self).setUp()
        if hasattr(self, '_test_case_group'):
            self.create_role()

    def create_role(self):
        self._test_case_role = Role.objects.create(label=TEST_CASE_ROLE_LABEL)

    def grant_permission(self, permission):
        self._test_case_role.grant(permission=permission)


class RoleTestMixin(object):
    def _create_test_role(self):
        self.test_role = Role.objects.create(label=TEST_ROLE_LABEL)

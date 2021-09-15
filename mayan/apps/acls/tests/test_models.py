from __future__ import absolute_import, unicode_literals

from django.core.exceptions import PermissionDenied
from django.db import models

from mayan.apps.common.tests import BaseTestCase
from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests import (
    DocumentTestMixin, TEST_DOCUMENT_TYPE_2_LABEL, TEST_DOCUMENT_TYPE_LABEL
)

from ..classes import ModelPermission
from ..models import AccessControlList

from .mixins import ACLTestMixin


class PermissionTestCase(DocumentTestMixin, BaseTestCase):
    auto_create_document_type = False

    def setUp(self):
        super(PermissionTestCase, self).setUp()
        self.test_document_type_1 = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        self.test_document_type_2 = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_2_LABEL
        )

        self.test_document_1 = self.upload_document(
            document_type=self.test_document_type_1
        )
        self.test_document_2 = self.upload_document(
            document_type=self.test_document_type_1
        )
        self.test_document_3 = self.upload_document(
            document_type=self.test_document_type_2
        )

    def test_check_access_without_permissions(self):
        with self.assertRaises(PermissionDenied):
            AccessControlList.objects.check_access(
                obj=self.test_document_1, permission=permission_document_view,
                user=self._test_case_user
            )

    def test_filtering_without_permissions(self):
        self.assertEqual(
            AccessControlList.objects.restrict_queryset(
                permission=permission_document_view,
                queryset=Document.objects.all(), user=self._test_case_user,
            ).count(), 0
        )

    def test_check_access_with_acl(self):
        acl = AccessControlList.objects.create(
            content_object=self.test_document_1, role=self._test_case_role
        )
        acl.permissions.add(permission_document_view.stored_permission)

        try:
            AccessControlList.objects.check_access(
                obj=self.test_document_1, permission=permission_document_view,
                user=self._test_case_user
            )
        except PermissionDenied:
            self.fail('PermissionDenied exception was not expected.')

    def test_filtering_with_permissions(self):
        acl = AccessControlList.objects.create(
            content_object=self.test_document_1, role=self._test_case_role
        )
        acl.permissions.add(permission_document_view.stored_permission)

        self.assertQuerysetEqual(
            AccessControlList.objects.restrict_queryset(
                permission=permission_document_view,
                queryset=Document.objects.all(), user=self._test_case_user
            ), (repr(self.test_document_1),)
        )

    def test_check_access_with_inherited_acl(self):
        acl = AccessControlList.objects.create(
            content_object=self.test_document_type_1, role=self._test_case_role
        )
        acl.permissions.add(permission_document_view.stored_permission)

        try:
            AccessControlList.objects.check_access(
                obj=self.test_document_1, permission=permission_document_view,
                user=self._test_case_user
            )
        except PermissionDenied:
            self.fail('PermissionDenied exception was not expected.')

    def test_check_access_with_inherited_acl_and_direct_acl(self):
        test_acl_1 = AccessControlList.objects.create(
            content_object=self.test_document_type_1, role=self._test_case_role
        )
        test_acl_1.permissions.add(permission_document_view.stored_permission)

        test_acl_2 = AccessControlList.objects.create(
            content_object=self.test_document_3, role=self._test_case_role
        )
        test_acl_2.permissions.add(permission_document_view.stored_permission)

        try:
            AccessControlList.objects.check_access(
                obj=self.test_document_3, permission=permission_document_view,
                user=self._test_case_user
            )
        except PermissionDenied:
            self.fail('PermissionDenied exception was not expected.')

    def test_filtering_with_inherited_permissions(self):
        acl = AccessControlList.objects.create(
            content_object=self.test_document_type_1, role=self._test_case_role
        )
        acl.permissions.add(permission_document_view.stored_permission)

        result = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view, queryset=Document.objects.all(),
            user=self._test_case_user
        )

        # Since document_1 and document_2 are of document_type_1
        # they are the only ones that should be returned
        self.assertTrue(self.test_document_1 in result)
        self.assertTrue(self.test_document_2 in result)
        self.assertTrue(self.test_document_3 not in result)

    def test_filtering_with_inherited_permissions_and_local_acl(self):
        self._test_case_role.permissions.add(
            permission_document_view.stored_permission
        )

        acl = AccessControlList.objects.create(
            content_object=self.test_document_type_1, role=self._test_case_role
        )
        acl.permissions.add(permission_document_view.stored_permission)

        acl = AccessControlList.objects.create(
            content_object=self.test_document_3, role=self._test_case_role
        )
        acl.permissions.add(permission_document_view.stored_permission)

        result = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view, queryset=Document.objects.all(),
            user=self._test_case_user,
        )
        self.assertTrue(self.test_document_1 in result)
        self.assertTrue(self.test_document_2 in result)
        self.assertTrue(self.test_document_3 in result)


class InheritedPermissionTestCase(ACLTestMixin, BaseTestCase):
    def test_retrieve_inherited_role_permission_not_model_applicable(self):
        self._create_test_model()
        self.test_object = self.TestModel.objects.create()
        self._create_test_acl()
        self._create_test_permission()

        self.test_role.grant(permission=self.test_permission)

        queryset = AccessControlList.objects.get_inherited_permissions(
            obj=self.test_object, role=self.test_role
        )
        self.assertTrue(self.test_permission.stored_permission not in queryset)

    def test_retrieve_inherited_role_permission_model_applicable(self):
        self._create_test_model()
        self.test_object = self.TestModel.objects.create()
        self._create_test_acl()
        self._create_test_permission()

        ModelPermission.register(
            model=self.test_object._meta.model, permissions=(
                self.test_permission,
            )
        )
        self.test_role.grant(permission=self.test_permission)

        queryset = AccessControlList.objects.get_inherited_permissions(
            obj=self.test_object, role=self.test_role
        )
        self.assertTrue(self.test_permission.stored_permission in queryset)

    def test_retrieve_inherited_related_parent_child_permission(self):
        self._create_test_permission()

        self._create_test_model(model_name='TestModelParent')
        self._create_test_model(
            fields={
                'parent': models.ForeignKey(
                    on_delete=models.CASCADE, related_name='children',
                    to='TestModelParent',
                )
            }, model_name='TestModelChild'
        )

        ModelPermission.register(
            model=self.TestModelParent, permissions=(
                self.test_permission,
            )
        )
        ModelPermission.register(
            model=self.TestModelChild, permissions=(
                self.test_permission,
            )
        )
        ModelPermission.register_inheritance(
            model=self.TestModelChild, related='parent',
        )

        parent = self.TestModelParent.objects.create()
        child = self.TestModelChild.objects.create(parent=parent)

        AccessControlList.objects.grant(
            obj=parent, permission=self.test_permission, role=self.test_role
        )

        queryset = AccessControlList.objects.get_inherited_permissions(
            obj=child, role=self.test_role
        )

        self.assertTrue(self.test_permission.stored_permission in queryset)

    def test_retrieve_inherited_related_grandparent_parent_child_permission(self):
        self._create_test_permission()

        self._create_test_model(model_name='TestModelGrandParent')
        self._create_test_model(
            fields={
                'parent': models.ForeignKey(
                    on_delete=models.CASCADE, related_name='children',
                    to='TestModelGrandParent',
                )
            }, model_name='TestModelParent'
        )
        self._create_test_model(
            fields={
                'parent': models.ForeignKey(
                    on_delete=models.CASCADE, related_name='children',
                    to='TestModelParent',
                )
            }, model_name='TestModelChild'
        )

        ModelPermission.register(
            model=self.TestModelGrandParent, permissions=(
                self.test_permission,
            )
        )
        ModelPermission.register(
            model=self.TestModelParent, permissions=(
                self.test_permission,
            )
        )
        ModelPermission.register(
            model=self.TestModelChild, permissions=(
                self.test_permission,
            )
        )

        ModelPermission.register_inheritance(
            model=self.TestModelChild, related='parent',
        )
        ModelPermission.register_inheritance(
            model=self.TestModelParent, related='parent',
        )

        grandparent = self.TestModelGrandParent.objects.create()
        parent = self.TestModelParent.objects.create(parent=grandparent)
        child = self.TestModelChild.objects.create(parent=parent)

        AccessControlList.objects.grant(
            obj=grandparent, permission=self.test_permission,
            role=self.test_role
        )

        queryset = AccessControlList.objects.get_inherited_permissions(
            obj=child, role=self.test_role
        )

        self.assertTrue(self.test_permission.stored_permission in queryset)


class MultipleAccessTestCase(ACLTestMixin, BaseTestCase):
    def setUp(self):
        super(MultipleAccessTestCase, self).setUp()
        self._create_test_permission()
        self._create_test_permission_2()

        self._create_test_model(model_name='TestModelParent1')
        self._create_test_model(model_name='TestModelParent2')
        self._create_test_model(
            fields={
                'parent_1': models.ForeignKey(
                    on_delete=models.CASCADE, related_name='children1',
                    to='TestModelParent1',
                ),
                'parent_2': models.ForeignKey(
                    on_delete=models.CASCADE, related_name='children2',
                    to='TestModelParent2',
                )
            }, model_name='TestModelChild'
        )

        ModelPermission.register(
            model=self.TestModelParent1, permissions=(
                self.test_permission,
            )
        )
        ModelPermission.register(
            model=self.TestModelParent2, permissions=(
                self.test_permission_2,
            )
        )

        self.test_object_parent_1 = self.TestModelParent1.objects.create()
        self.test_object_parent_2 = self.TestModelParent2.objects.create()
        self.test_object_child = self.TestModelChild.objects.create(
            parent_1=self.test_object_parent_1, parent_2=self.test_object_parent_2
        )

        ModelPermission.register_inheritance(
            model=self.TestModelChild, related='parent_1'
        )
        ModelPermission.register_inheritance(
            model=self.TestModelChild, related='parent_2'
        )

    def test_restrict_queryset_and_operator_first_permission(self):
        self.grant_access(obj=self.test_object_parent_1, permission=self.test_permission)

        queryset = AccessControlList.objects.restrict_queryset_by_accesses(
            operator=AccessControlList.OPERATOR_AND,
            permissions=(self.test_permission, self.test_permission_2),
            queryset=self.TestModelChild.objects.all(),
            user=self._test_case_user
        )
        self.assertTrue(self.test_object_child not in queryset)

    def test_restrict_queryset_and_operator_second_permission(self):
        self.grant_access(obj=self.test_object_parent_2, permission=self.test_permission_2)

        queryset = AccessControlList.objects.restrict_queryset_by_accesses(
            operator=AccessControlList.OPERATOR_AND,
            permissions=(self.test_permission, self.test_permission_2),
            queryset=self.TestModelChild.objects.all(),
            user=self._test_case_user
        )
        self.assertTrue(self.test_object_child not in queryset)

    def test_restrict_queryset_and_operator_both_permissions(self):
        self.grant_access(obj=self.test_object_parent_1, permission=self.test_permission)
        self.grant_access(obj=self.test_object_parent_2, permission=self.test_permission_2)

        queryset = AccessControlList.objects.restrict_queryset_by_accesses(
            operator=AccessControlList.OPERATOR_AND,
            permissions=(self.test_permission, self.test_permission_2),
            queryset=self.TestModelChild.objects.all(),
            user=self._test_case_user
        )
        self.assertTrue(self.test_object_child in queryset)

    def test_restrict_queryset_or_operator_first_permission(self):
        self.grant_access(obj=self.test_object_parent_1, permission=self.test_permission)

        queryset = AccessControlList.objects.restrict_queryset_by_accesses(
            operator=AccessControlList.OPERATOR_OR,
            permissions=(self.test_permission, self.test_permission_2),
            queryset=self.TestModelChild.objects.all(),
            user=self._test_case_user
        )
        self.assertTrue(self.test_object_child in queryset)

    def test_restrict_queryset_or_operator_second_permission(self):
        self.grant_access(obj=self.test_object_parent_2, permission=self.test_permission_2)

        queryset = AccessControlList.objects.restrict_queryset_by_accesses(
            operator=AccessControlList.OPERATOR_OR,
            permissions=(self.test_permission, self.test_permission_2),
            queryset=self.TestModelChild.objects.all(),
            user=self._test_case_user
        )
        self.assertTrue(self.test_object_child in queryset)

    def test_restrict_queryset_or_operator_both_permissions(self):
        self.grant_access(obj=self.test_object_parent_1, permission=self.test_permission)
        self.grant_access(obj=self.test_object_parent_2, permission=self.test_permission_2)

        queryset = AccessControlList.objects.restrict_queryset_by_accesses(
            operator=AccessControlList.OPERATOR_OR,
            permissions=(self.test_permission, self.test_permission_2),
            queryset=self.TestModelChild.objects.all(),
            user=self._test_case_user
        )
        self.assertTrue(self.test_object_child in queryset)

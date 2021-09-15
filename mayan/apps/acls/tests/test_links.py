from __future__ import unicode_literals

from django.urls import reverse

from mayan.apps.common.tests import GenericViewTestCase

from ..links import (
    link_acl_create, link_acl_delete, link_acl_list, link_acl_permissions
)
from ..permissions import permission_acl_edit, permission_acl_view

from .mixins import ACLTestMixin


class AccessControlListLinksTestCase(ACLTestMixin, GenericViewTestCase):
    auto_create_test_role = False

    def setUp(self):
        super(AccessControlListLinksTestCase, self).setUp()
        self._setup_test_object()

    def test_object_acl_create_link(self):
        self.grant_access(obj=self.test_object, permission=permission_acl_edit)

        self.add_test_view(test_object=self.test_object)
        context = self.get_test_view()
        resolved_link = link_acl_create.resolve(context=context)

        self.assertNotEqual(resolved_link, None)

        self.assertEqual(
            resolved_link.url, reverse(
                viewname='acls:acl_create',
                kwargs=self.test_content_object_view_kwargs
            )
        )

    def test_object_acl_delete_link(self):
        self.grant_access(obj=self.test_object, permission=permission_acl_edit)

        self.add_test_view(test_object=self._test_case_acl)
        context = self.get_test_view()
        resolved_link = link_acl_delete.resolve(context=context)

        self.assertNotEqual(resolved_link, None)

        self.assertEqual(
            resolved_link.url, reverse(
                viewname='acls:acl_delete',
                kwargs={'acl_id': self._test_case_acl.pk}
            )
        )

    def test_object_acl_edit_link(self):
        self.grant_access(obj=self.test_object, permission=permission_acl_edit)

        self.add_test_view(test_object=self._test_case_acl)
        context = self.get_test_view()
        resolved_link = link_acl_permissions.resolve(context=context)

        self.assertNotEqual(resolved_link, None)

        self.assertEqual(
            resolved_link.url, reverse(
                viewname='acls:acl_permissions',
                kwargs={'acl_id': self._test_case_acl.pk}
            )
        )

    def test_object_acl_list_link(self):
        self.grant_access(obj=self.test_object, permission=permission_acl_view)

        self.add_test_view(test_object=self.test_object)
        context = self.get_test_view()
        resolved_link = link_acl_list.resolve(context=context)

        self.assertNotEqual(resolved_link, None)

        self.assertEqual(
            resolved_link.url, reverse(
                viewname='acls:acl_list',
                kwargs=self.test_content_object_view_kwargs
            )
        )

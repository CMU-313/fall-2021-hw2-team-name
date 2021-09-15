from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import status

from mayan.apps.rest_api.tests import BaseAPITestCase

from ..permissions import (
    permission_group_create, permission_group_delete,
    permission_group_edit, permission_group_view,
    permission_user_create, permission_user_delete,
    permission_user_edit, permission_user_view
)

from .mixins import (
    GroupAPITestMixin, GroupTestMixin, UserAPITestMixin, UserTestMixin
)


class GroupAPITestCase(GroupAPITestMixin, GroupTestMixin, UserTestMixin, BaseAPITestCase):
    def test_group_create_api_view_no_permission(self):
        group_count = Group.objects.count()

        response = self._request_test_group_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(group_count, Group.objects.count())

    def test_group_create_api_view_with_permission(self):
        group_count = Group.objects.count()

        self.grant_permission(permission=permission_group_create)
        response = self._request_test_group_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertNotEqual(group_count, Group.objects.count())

    def test_group_delete_api_view_no_permission(self):
        self._create_test_group()

        group_count = Group.objects.count()

        response = self._request_test_group_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(group_count, Group.objects.count())

    def test_group_delete_api_view_with_access(self):
        self._create_test_group()

        group_count = Group.objects.count()

        self.grant_access(
            obj=self.test_group, permission=permission_group_delete
        )
        response = self._request_test_group_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertNotEqual(group_count, Group.objects.count())

    def test_group_detail_api_view_no_permission(self):
        self._create_test_group()

        response = self._request_test_group_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertNotEqual(
            self.test_group.name, response.data.get('name', None)
        )

    def test_group_detail_api_view_with_access(self):
        self._create_test_group()

        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_test_group_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.test_group.name, response.data.get('name', None))

    def test_group_edit_patch_api_view_no_permission(self):
        self._create_test_group()

        group_name = self.test_group.name

        response = self._request_test_group_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_group.refresh_from_db()
        self.assertEqual(group_name, self.test_group.name)

    def test_group_edit_patch_with_access(self):
        self._create_test_group()

        group_name = self.test_group.name

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_test_group_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_group.refresh_from_db()
        self.assertNotEqual(group_name, self.test_group.name)

    def test_group_list_api_view_no_permission(self):
        self._create_test_group()

        response = self._request_test_group_list_api_view()
        self.assertNotContains(
            response=response, text=self.test_group.name,
            status_code=status.HTTP_200_OK
        )

    def test_group_list_api_view_with_access(self):
        self._create_test_group()

        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_test_group_list_api_view()
        self.assertContains(
            response=response, text=self.test_group.name,
            status_code=status.HTTP_200_OK
        )

    def _setup_group_user_add(self):
        self._create_test_group()
        self._create_test_user()

    def test_group_user_add_api_view_no_permission(self):
        self._setup_group_user_add()

        response = self._request_test_group_user_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user not in self.test_group.user_set.all())

    def test_group_user_add_with_group_access(self):
        self._setup_group_user_add()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_test_group_user_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user not in self.test_group.user_set.all())

    def test_group_user_add_with_user_access(self):
        self._setup_group_user_add()

        self.grant_access(
            obj=self.test_user, permission=permission_user_edit
        )
        response = self._request_test_group_user_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user not in self.test_group.user_set.all())

    def test_group_user_add_with_full_access(self):
        self._setup_group_user_add()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        self.grant_access(
            obj=self.test_user, permission=permission_user_edit
        )
        response = self._request_test_group_user_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user in self.test_group.user_set.all())

    def _setup_group_user_list(self):
        self._create_test_group()
        self._create_test_user()
        self.test_group.user_set.add(self.test_user)

    def test_group_user_list_api_view_no_permission(self):
        self._setup_group_user_list()

        response = self._request_test_group_user_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('count' not in response.json())

    def test_group_user_list_with_group_access(self):
        self._setup_group_user_list()

        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_test_group_user_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json()['count'], 0)

    def test_group_user_list_with_user_access(self):
        self._setup_group_user_list()

        self.grant_access(
            obj=self.test_user, permission=permission_user_view
        )
        response = self._request_test_group_user_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('count' not in response.json())

    def test_group_user_list_with_full_access(self):
        self._setup_group_user_list()

        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        self.grant_access(
            obj=self.test_user, permission=permission_user_view
        )
        response = self._request_test_group_user_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json()['count'], 1)

    def _setup_group_user_remove(self):
        self._create_test_group()
        self._create_test_user()
        self.test_group.user_set.add(self.test_user)

    def test_group_user_remove_api_view_no_permission(self):
        self._setup_group_user_remove()

        response = self._request_test_group_user_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user in self.test_group.user_set.all())

    def test_group_user_remove_with_group_access(self):
        self._setup_group_user_remove()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_test_group_user_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user in self.test_group.user_set.all())

    def test_group_user_remove_with_user_access(self):
        self._setup_group_user_remove()

        self.grant_access(
            obj=self.test_user, permission=permission_user_edit
        )
        response = self._request_test_group_user_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user in self.test_group.user_set.all())

    def test_group_user_remove_with_full_access(self):
        self._setup_group_user_remove()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        self.grant_access(
            obj=self.test_user, permission=permission_user_edit
        )
        response = self._request_test_group_user_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_group.refresh_from_db()
        self.assertTrue(self.test_user not in self.test_group.user_set.all())


class UserAPITestCase(UserAPITestMixin, GroupTestMixin, UserTestMixin, BaseAPITestCase):
    def test_user_create_api_view_no_permission(self):
        user_count = get_user_model().objects.count()

        response = self._request_test_user_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(user_count, get_user_model().objects.count())

    def test_user_create_api_view_with_permission(self):
        user_count = get_user_model().objects.count()

        self.grant_permission(permission=permission_user_create)
        response = self._request_test_user_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(user_count + 1, get_user_model().objects.count())

    def test_user_create_api_view_login(self):
        self._create_test_user()

        self.assertTrue(
            self.login(
                username=self.test_user.username,
                password=self.test_user.clear_password
            )
        )

    def test_user_create_login_password_change_api_view_no_permission(self):
        self._create_test_user()
        self._request_test_user_password_change_api_view()

        self.assertFalse(
            self.login(
                username=self.test_user.username,
                password=self.test_user.clear_password
            )
        )

    def test_user_create_login_password_change_api_view_with_access(self):
        self._create_test_user()

        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        self._request_test_user_password_change_api_view()

        self.assertTrue(
            self.login(
                username=self.test_user.username,
                password=self.test_user.clear_password
            )
        )

    def test_user_edit_put_api_view_no_permission(self):
        self._create_test_user()
        username = self.test_user.username

        response = self._request_test_user_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_user.refresh_from_db()
        self.assertEqual(username, self.test_user.username)

    def test_user_edit_put_api_view_with_access(self):
        self._create_test_user()
        username = self.test_user.username

        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        response = self._request_test_user_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_user.refresh_from_db()
        self.assertNotEqual(username, self.test_user.username)

    def test_user_edit_patch_api_view_no_permission(self):
        self._create_test_user()
        username = self.test_user.username

        response = self._request_test_user_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_user.refresh_from_db()
        self.assertEqual(username, self.test_user.username)

    def test_user_edit_patch_api_view_with_access(self):
        self._create_test_user()
        username = self.test_user.username

        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        response = self._request_test_user_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_user.refresh_from_db()
        self.assertNotEqual(username, self.test_user.username)

    def test_user_delete_api_view_no_permission(self):
        self._create_test_user()

        response = self._request_test_user_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(
            get_user_model().objects.filter(pk=self.test_user.pk).exists()
        )

    def test_user_delete_api_view_with_access(self):
        self._create_test_user()

        self.grant_access(
            obj=self.test_user, permission=permission_user_delete
        )
        response = self._request_test_user_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            get_user_model().objects.filter(pk=self.test_user.pk).exists()
        )

    def _setup_user_group_list(self):
        self._create_test_group()
        self._create_test_user()
        self.test_user.groups.add(self.test_group)

    def test_user_group_list_api_view_no_permission(self):
        self._setup_user_group_list()

        response = self._request_test_user_group_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_group_list_api_view_with_user_access(self):
        self._setup_user_group_list()

        self.grant_access(obj=self.test_user, permission=permission_user_view)
        response = self._request_test_user_group_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_user_group_list_api_view_with_group_access(self):
        self._setup_user_group_list()

        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_test_user_group_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_group_list_api_view_with_full_access(self):
        self._setup_user_group_list()

        self.grant_access(obj=self.test_user, permission=permission_user_view)
        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_test_user_group_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def _setup_user_group_add(self):
        self._create_test_group()
        self._create_test_user()

    def test_user_group_add_api_view_no_permission(self):
        self._setup_user_group_add()

        response = self._request_test_user_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_user.refresh_from_db()
        self.assertTrue(self.test_group not in self.test_user.groups.all())

    def test_user_group_add_api_view_with_user_access(self):
        self._setup_user_group_add()

        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        response = self._request_test_user_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_user.refresh_from_db()
        self.assertTrue(self.test_group not in self.test_user.groups.all())

    def test_user_group_add_api_view_with_group_access(self):
        self._setup_user_group_add()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_test_user_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_user.refresh_from_db()
        self.assertTrue(self.test_group not in self.test_user.groups.all())

    def test_user_group_add_api_view_with_full_access(self):
        self._setup_user_group_add()

        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_test_user_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_user.refresh_from_db()
        self.assertTrue(self.test_group in self.test_user.groups.all())

    def _setup_user_group_remove(self):
        self._create_test_group()
        self._create_test_user()
        self.test_user.groups.add(self.test_group)

    def test_user_group_remove_api_view_no_permission(self):
        self._setup_user_group_remove()

        response = self._request_test_user_group_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_user.refresh_from_db()
        self.assertTrue(self.test_group in self.test_user.groups.all())

    def test_user_group_remove_api_view_with_user_access(self):
        self._setup_user_group_remove()

        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        response = self._request_test_user_group_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_user.refresh_from_db()
        self.assertTrue(self.test_group in self.test_user.groups.all())

    def test_user_group_remove_api_view_with_group_access(self):
        self._setup_user_group_remove()

        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_test_user_group_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_user.refresh_from_db()
        self.assertTrue(self.test_group in self.test_user.groups.all())

    def test_user_group_remove_api_view_with_full_access(self):
        self._setup_user_group_remove()

        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_test_user_group_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_user.refresh_from_db()
        self.assertTrue(self.test_group not in self.test_user.groups.all())

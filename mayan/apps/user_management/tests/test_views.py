from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from mayan.apps.common.tests import GenericViewTestCase
from mayan.apps.documents.tests import GenericDocumentViewTestCase
from mayan.apps.metadata.models import MetadataType
from mayan.apps.metadata.permissions import permission_metadata_edit
from mayan.apps.metadata.tests.literals import (
    TEST_METADATA_TYPE_LABEL, TEST_METADATA_TYPE_NAME,
)

from ..permissions import (
    permission_group_create, permission_group_delete, permission_group_edit,
    permission_group_view, permission_user_create, permission_user_delete,
    permission_user_edit, permission_user_view
)

from .literals import (
    TEST_GROUP_NAME, TEST_GROUP_NAME_EDITED, TEST_USER_PASSWORD_EDITED,
    TEST_USER_USERNAME
)
from .mixins import (
    GroupTestMixin, GroupViewTestMixin, UserTestMixin, UserViewTestMixin
)

TEST_USER_TO_DELETE_USERNAME = 'user_to_delete'


class GroupViewsTestCase(GroupTestMixin, GroupViewTestMixin, UserTestMixin, GenericViewTestCase):
    def test_group_create_view_no_permission(self):
        response = self._request_test_group_create_view()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Group.objects.count(), 1)

    def test_group_create_view_with_permission(self):
        self.grant_permission(permission=permission_group_create)
        response = self._request_test_group_create_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Group.objects.count(), 2)

    def test_group_delete_view_no_permission(self):
        self._create_test_group()
        response = self._request_test_group_delete_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Group.objects.count(), 2)

    def test_group_delete_view_with_access(self):
        self._create_test_group()
        self.grant_access(
            obj=self.test_group, permission=permission_group_delete
        )
        response = self._request_test_group_delete_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Group.objects.count(), 1)

    def test_group_edit_view_no_permission(self):
        self._create_test_group()
        response = self._request_test_group_edit_view()
        self.assertEqual(response.status_code, 404)
        self.test_group.refresh_from_db()
        self.assertEqual(self.test_group.name, TEST_GROUP_NAME)

    def test_group_edit_view_with_access(self):
        self._create_test_group()
        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_test_group_edit_view()
        self.assertEqual(response.status_code, 302)
        self.test_group.refresh_from_db()
        self.assertEqual(self.test_group.name, TEST_GROUP_NAME_EDITED)

    def test_group_list_view_no_permission(self):
        self._create_test_group()
        response = self._request_test_group_list_view()
        self.assertNotContains(
            response=response, text=self.test_group.name, status_code=200
        )

    def test_group_list_view_with_permission(self):
        self._create_test_group()
        self.grant_access(
            obj=self.test_group, permission=permission_group_view
        )
        response = self._request_test_group_list_view()
        self.assertContains(
            response=response, text=self.test_group.name, status_code=200
        )

    def test_group_members_view_no_permission(self):
        self._create_test_user()
        self._create_test_group()
        self.test_user.groups.add(self.test_group)
        response = self._request_test_group_members_view()
        self.assertEqual(response.status_code, 404)

    def test_group_members_view_with_group_access(self):
        self._create_test_user()
        self._create_test_group()
        self.test_user.groups.add(self.test_group)
        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_test_group_members_view()
        self.assertContains(
            response=response, text=self.test_group.name, status_code=200
        )
        self.assertNotContains(
            response=response, text=self.test_user.username, status_code=200
        )

    def test_group_members_view_with_user_access(self):
        self._create_test_user()
        self._create_test_group()
        self.test_user.groups.add(self.test_group)
        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        response = self._request_test_group_members_view()
        self.assertNotContains(
            response=response, text=self.test_group.name, status_code=404
        )

    def test_group_members_view_with_full_access(self):
        self._create_test_user()
        self._create_test_group()
        self.test_user.groups.add(self.test_group)
        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        response = self._request_test_group_members_view()
        self.assertContains(
            response=response, text=self.test_user.username, status_code=200
        )
        self.assertContains(
            response=response, text=self.test_group.name, status_code=200
        )


class UserViewsTestCase(GroupTestMixin, UserTestMixin, UserViewTestMixin, GenericViewTestCase):
    def test_user_create_view_no_permission(self):
        user_count = get_user_model().objects.count()

        response = self._request_test_user_create_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(get_user_model().objects.count(), user_count)
        self.assertFalse(TEST_USER_USERNAME in get_user_model().objects.values_list('username', flat=True))

    def test_user_create_view_with_permission(self):
        user_count = get_user_model().objects.count()

        self.grant_permission(permission=permission_user_create)
        response = self._request_test_user_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(get_user_model().objects.count(), user_count + 1)
        self.assertTrue(TEST_USER_USERNAME in get_user_model().objects.values_list('username', flat=True))

    def test_user_delete_view_no_access(self):
        self._create_test_user()
        user_count = get_user_model().objects.count()

        response = self._request_test_user_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(get_user_model().objects.count(), user_count)

    def test_user_delete_view_with_access(self):
        self._create_test_user()
        user_count = get_user_model().objects.count()

        self.grant_access(
            obj=self.test_user, permission=permission_user_delete
        )
        response = self._request_test_user_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(get_user_model().objects.count(), user_count - 1)

    def test_superuser_delete_view_with_access(self):
        self._create_test_superuser()

        superuser_count = get_user_model().objects.filter(is_superuser=True).count()
        self.grant_access(
            obj=self.test_superuser, permission=permission_user_delete
        )
        response = self._request_test_superuser_delete_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            get_user_model().objects.filter(is_superuser=True).count(),
            superuser_count
        )

    def test_superuser_detail_view_with_access(self):
        self._create_test_superuser()

        self.grant_access(
            obj=self.test_superuser, permission=permission_user_view
        )
        response = self._request_test_superuser_detail_view()
        self.assertEqual(response.status_code, 404)

    def test_user_groups_view_no_permission(self):
        self._create_test_user()
        self._create_test_group()
        self.test_user.groups.add(self.test_group)
        response = self._request_test_user_groups_view()
        self.assertEqual(response.status_code, 404)

    def test_user_groups_view_with_group_access(self):
        self._create_test_user()
        self._create_test_group()
        self.test_user.groups.add(self.test_group)
        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        response = self._request_test_user_groups_view()
        self.assertNotContains(
            response=response, text=self.test_user.username, status_code=404
        )

    def test_user_groups_view_with_user_access(self):
        self._create_test_user()
        self._create_test_group()
        self.test_user.groups.add(self.test_group)
        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        response = self._request_test_user_groups_view()
        self.assertContains(
            response=response, text=self.test_user.username, status_code=200
        )
        self.assertNotContains(
            response=response, text=self.test_group.name, status_code=200
        )

    def test_user_groups_view_with_full_access(self):
        self._create_test_user()
        self._create_test_group()
        self.test_user.groups.add(self.test_group)
        self.grant_access(
            obj=self.test_group, permission=permission_group_edit
        )
        self.grant_access(obj=self.test_user, permission=permission_user_edit)
        response = self._request_test_user_groups_view()

        self.assertContains(
            response=response, text=self.test_user.username, status_code=200
        )
        self.assertContains(
            response=response, text=self.test_group.name, status_code=200
        )

    def _request_set_password_view(self, password):
        return self.post(
            viewname='user_management:user_set_password',
            kwargs={'user_id': self.test_user.pk},
            data={
                'new_password1': password, 'new_password2': password
            }
        )

    def test_user_set_password_view_no_access(self):
        self._create_test_user()
        response = self._request_set_password_view(
            password=TEST_USER_PASSWORD_EDITED
        )

        self.assertEqual(response.status_code, 404)

        self.logout()

        result = self.login(
            username=self.test_user.username,
            password=TEST_USER_PASSWORD_EDITED
        )

        self.assertFalse(result)

        response = self.get(viewname='user_management:current_user_details')

        self.assertEqual(response.status_code, 302)

    def test_user_set_password_view_with_access(self):
        self._create_test_user()
        self.grant_access(obj=self.test_user, permission=permission_user_edit)

        response = self._request_set_password_view(
            password=TEST_USER_PASSWORD_EDITED
        )

        self.assertEqual(response.status_code, 302)

        self.logout()
        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD_EDITED
        )
        response = self.get(viewname='user_management:current_user_details')

        self.assertEqual(response.status_code, 200)

    def _request_multiple_user_set_password_view(self, password):
        return self.post(
            viewname='user_management:user_multiple_set_password',
            data={
                'id_list': self.test_user.pk,
                'new_password1': password,
                'new_password2': password
            }
        )

    def test_user_multiple_set_password_view_no_access(self):
        self._create_test_user()
        response = self._request_multiple_user_set_password_view(
            password=TEST_USER_PASSWORD_EDITED
        )

        self.assertEqual(response.status_code, 404)

        self.logout()

        result = self.login(
            username=self.test_user.username,
            password=TEST_USER_PASSWORD_EDITED
        )

        self.assertFalse(result)

        response = self.get(viewname='user_management:current_user_details')
        self.assertEqual(response.status_code, 302)

    def test_user_multiple_set_password_view_with_access(self):
        self._create_test_user()
        self.grant_access(obj=self.test_user, permission=permission_user_edit)

        response = self._request_multiple_user_set_password_view(
            password=TEST_USER_PASSWORD_EDITED
        )

        self.assertEqual(response.status_code, 302)

        self.logout()
        self.login(
            username=self.test_user.username, password=TEST_USER_PASSWORD_EDITED
        )
        response = self.get(viewname='user_management:current_user_details')

        self.assertEqual(response.status_code, 200)

    def _request_test_user_multiple_delete_view(self):
        return self.post(
            viewname='user_management:user_multiple_delete', data={
                'id_list': self.test_user.pk
            }
        )

    def test_user_multiple_delete_view_no_access(self):
        self._create_test_user()
        user_count = get_user_model().objects.count()

        response = self._request_test_user_multiple_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(get_user_model().objects.count(), user_count)

    def test_user_multiple_delete_view_with_access(self):
        self._create_test_user()
        user_count = get_user_model().objects.count()

        self.grant_access(
            obj=self.test_user, permission=permission_user_delete
        )
        response = self._request_test_user_multiple_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(get_user_model().objects.count(), user_count - 1)


class MetadataLookupIntegrationTestCase(GenericDocumentViewTestCase):
    def setUp(self):
        super(MetadataLookupIntegrationTestCase, self).setUp()
        self.metadata_type = MetadataType.objects.create(
            name=TEST_METADATA_TYPE_NAME, label=TEST_METADATA_TYPE_LABEL
        )

        self.document_type.metadata.create(metadata_type=self.metadata_type)

        self.login_user()

    def test_user_list_lookup_render(self):
        self.metadata_type.lookup = '{{ users }}'
        self.metadata_type.save()
        self.document.metadata.create(metadata_type=self.metadata_type)
        self.grant_access(
            obj=self.document, permission=permission_metadata_edit
        )

        response = self.get(
            viewname='metadata:document_metadata_edit',
            kwargs={'document_id': self.document.pk}
        )
        self.assertContains(
            response=response, text='<option value="{}">{}</option>'.format(
                TEST_USER_USERNAME, TEST_USER_USERNAME
            ), status_code=200
        )

    def test_group_list_lookup_render(self):
        self.metadata_type.lookup = '{{ groups }}'
        self.metadata_type.save()
        self.document.metadata.create(metadata_type=self.metadata_type)
        self.grant_access(
            obj=self.document, permission=permission_metadata_edit
        )

        response = self.get(
            viewname='metadata:document_metadata_edit',
            kwargs={'document_id': self.document.pk}
        )

        self.assertContains(
            response=response, text='<option value="{}">{}</option>'.format(
                Group.objects.first().name, Group.objects.first().name
            ), status_code=200
        )

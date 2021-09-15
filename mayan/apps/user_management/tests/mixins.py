from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .literals import (
    TEST_GROUP_2_NAME, TEST_GROUP_2_NAME_EDITED, TEST_USER_2_EMAIL,
    TEST_USER_2_PASSWORD, TEST_USER_2_USERNAME, TEST_USER_2_USERNAME_EDITED
)


class UserTestMixin(object):
    def _create_test_group(self):
        self.test_group = Group.objects.create(name=TEST_GROUP_2_NAME)

    def _edit_test_group(self):
        self.test_group.name = TEST_GROUP_2_NAME_EDITED
        self.test_group.save()

    def _create_test_user(self):
        self.test_user = get_user_model().objects.create(
            username=TEST_USER_2_USERNAME, email=TEST_USER_2_EMAIL,
            password=TEST_USER_2_PASSWORD
        )

    def _request_test_group_create_view(self):
        reponse = self.post(
            viewname='user_management:group_create', data={
                'name': TEST_GROUP_2_NAME
            }
        )
        self.test_group = Group.objects.filter(name=TEST_GROUP_2_NAME).first()
        return reponse

    def _request_test_group_edit_view(self):
        return self.post(
            viewname='user_management:group_edit', kwargs={
                'pk': self.test_group.pk
            }, data={
                'name': TEST_GROUP_2_NAME_EDITED
            }
        )

    def _request_test_user_create_view(self):
        reponse = self.post(
            viewname='user_management:user_create', data={
                'username': TEST_USER_2_USERNAME
            }
        )

        self.test_user = get_user_model().objects.filter(
            username=TEST_USER_2_USERNAME
        ).first()
        return reponse

    def _request_test_user_edit_view(self):
        return self.post(
            viewname='user_management:user_edit', kwargs={
                'pk': self.test_user.pk
            }, data={
                'username': TEST_USER_2_USERNAME_EDITED
            }
        )

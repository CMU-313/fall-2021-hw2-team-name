from __future__ import unicode_literals

from actstream.models import Action

from mayan.apps.common.tests import GenericViewTestCase

from ..events import (
    event_group_created, event_group_edited, event_user_created,
    event_user_edited
)

from .mixins import UserTestMixin


class GroupEventsTestCase(UserTestMixin, GenericViewTestCase):
    auto_create_group = False

    def test_group_create_event(self):
        self.login_admin_user()
        Action.objects.all().delete()
        self._request_test_group_create_view()
        self.assertEqual(Action.objects.last().target, self.test_group)
        self.assertEqual(Action.objects.last().verb, event_group_created.id)

    def test_group_edit_event(self):
        self.login_admin_user()
        self._create_test_group()
        Action.objects.all().delete()
        self._request_test_group_edit_view()
        self.assertEqual(Action.objects.last().target, self.test_group)
        self.assertEqual(Action.objects.last().verb, event_group_edited.id)


class UserEventsTestCase(UserTestMixin, GenericViewTestCase):
    auto_create_group = False

    def test_user_create_event(self):
        self.login_admin_user()
        Action.objects.all().delete()
        self._request_test_user_create_view()
        self.assertEqual(Action.objects.last().target, self.test_user)
        self.assertEqual(Action.objects.last().verb, event_user_created.id)

    def test_user_edit_event(self):
        self.login_admin_user()
        self._create_test_user()
        Action.objects.all().delete()
        self._request_test_user_edit_view()
        self.assertEqual(Action.objects.last().target, self.test_user)
        self.assertEqual(Action.objects.last().verb, event_user_edited.id)

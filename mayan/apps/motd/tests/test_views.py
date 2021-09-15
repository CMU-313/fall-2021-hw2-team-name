from __future__ import unicode_literals

from django.utils.encoding import force_text

from mayan.apps.common.tests import GenericViewTestCase

from ..models import Message
from ..permissions import (
    permission_message_create, permission_message_delete,
    permission_message_edit, permission_message_view
)

from .literals import (
    TEST_MESSAGE_LABEL, TEST_MESSAGE_LABEL_EDITED, TEST_MESSAGE_TEXT,
    TEST_MESSAGE_TEXT_EDITED
)
from .mixins import MOTDTestMixin


class MOTDViewTestCase(MOTDTestMixin, GenericViewTestCase):
    def test_message_create_view_no_permissions(self):
        response = self._request_message_create_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(Message.objects.count(), 0)

    def test_message_create_view_with_permissions(self):
        self.grant_permission(permission=permission_message_create)
        response = self._request_message_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Message.objects.count(), 1)
        message = Message.objects.first()
        self.assertEqual(message.label, TEST_MESSAGE_LABEL)
        self.assertEqual(message.message, TEST_MESSAGE_TEXT)

    def test_message_delete_view_no_permissions(self):
        self._create_test_message()

        response = self._request_message_delete_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Message.objects.count(), 1)

    def test_message_delete_view_with_access(self):
        self._create_test_message()

        self.grant_access(
            obj=self.test_message, permission=permission_message_delete
        )

        response = self._request_message_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Message.objects.count(), 0)

    def test_message_edit_view_no_permissions(self):
        self._create_test_message()

        response = self._request_message_edit_view()
        self.assertEqual(response.status_code, 404)
        self.test_message.refresh_from_db()
        self.assertEqual(self.test_message.label, TEST_MESSAGE_LABEL)
        self.assertEqual(self.test_message.message, TEST_MESSAGE_TEXT)

    def test_message_edit_view_with_access(self):
        self._create_test_message()

        self.grant_access(
            obj=self.test_message, permission=permission_message_edit
        )

        response = self._request_message_edit_view()
        self.assertEqual(response.status_code, 302)
        self.test_message.refresh_from_db()
        self.assertEqual(self.test_message.label, TEST_MESSAGE_LABEL_EDITED)
        self.assertEqual(
            self.test_message.message, TEST_MESSAGE_TEXT_EDITED
        )

    def test_message_list_view_no_permissions(self):
        self._create_test_message()

        response = self._request_message_list_view()
        self.assertNotContains(
            response=response, text=force_text(self.test_message),
            status_code=200
        )

    def test_message_list_view_with_access(self):
        self._create_test_message()

        self.grant_access(
            obj=self.test_message, permission=permission_message_view
        )

        response = self._request_message_list_view()
        self.assertContains(
            response=response, text=force_text(self.test_message),
            status_code=200
        )

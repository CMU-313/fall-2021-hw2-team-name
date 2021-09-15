from __future__ import unicode_literals

from actstream.models import Action

from mayan.apps.documents.tests import GenericDocumentViewTestCase

from ..events import (
    event_document_comment_created, event_document_comment_deleted
)
from ..permissions import permission_comment_create, permission_comment_delete

from .mixins import CommentsTestMixin


class CommentEventsTestCase(CommentsTestMixin, GenericDocumentViewTestCase):
    def test_comment_created_event_no_permissions(self):
        Action.objects.all().delete()

        response = self._request_document_comment_add_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Action.objects.count(), 0)

    def test_comment_created_event_with_permissions(self):
        Action.objects.all().delete()

        self.grant_access(
            obj=self.document, permission=permission_comment_create
        )
        response = self._request_document_comment_add_view()
        self.assertEqual(response.status_code, 302)

        event = Action.objects.first()

        self.assertEqual(event.verb, event_document_comment_created.id)
        self.assertEqual(event.action_object, self.document)
        self.assertEqual(event.target, self.test_comment)
        self.assertEqual(event.actor, self._test_case_user)

    def test_comment_deleted_event_no_permissions(self):
        self._create_comment()
        Action.objects.all().delete()

        response = self._request_document_comment_delete_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Action.objects.count(), 0)

    def test_comment_deleted_event_with_access(self):
        self._create_comment()
        Action.objects.all().delete()

        self.grant_access(
            obj=self.document, permission=permission_comment_delete
        )

        response = self._request_document_comment_delete_view()
        self.assertEqual(response.status_code, 302)
        event = Action.objects.first()

        self.assertEqual(event.verb, event_document_comment_deleted.id)
        self.assertEqual(event.target, self.document)
        self.assertEqual(event.actor, self._test_case_user)

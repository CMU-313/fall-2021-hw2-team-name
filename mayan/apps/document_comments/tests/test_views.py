from __future__ import unicode_literals

from mayan.apps.documents.tests import GenericDocumentViewTestCase

from ..permissions import (
    permission_comment_create, permission_comment_delete,
    permission_comment_view
)

from .literals import TEST_COMMENT_TEXT
from .mixins import CommentsTestMixin


class CommentsViewsTestCase(CommentsTestMixin, GenericDocumentViewTestCase):
    def test_document_comment_add_view_no_permission(self):
        response = self._request_document_comment_add_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.document.comments.all().count(), 0)

    def test_document_comment_add_view_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_comment_create
        )
        response = self._request_document_comment_add_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.document.comments.all().count(), 1)

    def _create_test_comment(self):
        self.test_comment = self.document.comments.create(
            user=self._test_case_user, comment=TEST_COMMENT_TEXT
        )

    def test_document_comment_delete_view_no_permission(self):
        self._create_test_comment()

        response = self._request_document_comment_delete_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.document.comments.all().count(), 1)

    def test_document_comment_delete_view_with_access(self):
        self._create_test_comment()

        self.grant_access(
            obj=self.document, permission=permission_comment_delete
        )
        response = self._request_document_comment_delete_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.document.comments.all().count(), 0)

    def _request_document_comment_list_view(self):
        return self.get(
            viewname='comments:comments_for_document',
            kwargs={'document_id': self.document.pk}
        )

    def test_document_comment_list_view_no_permissions(self):
        self._create_test_comment()

        response = self._request_document_comment_list_view()
        self.assertNotContains(
            response=response, status_code=404, text=TEST_COMMENT_TEXT
        )

    def test_document_comment_list_view_with_access(self):
        self._create_test_comment()

        self.grant_access(
            obj=self.document, permission=permission_comment_view
        )
        response = self._request_document_comment_list_view()
        self.assertContains(
            response=response, status_code=200, text=TEST_COMMENT_TEXT
        )

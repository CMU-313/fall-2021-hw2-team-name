from __future__ import unicode_literals

from rest_framework import status

from mayan.apps.documents.tests import DocumentTestMixin
from mayan.apps.rest_api.tests import BaseAPITestCase

from ..models import Comment
from ..permissions import (
    permission_comment_create, permission_comment_delete,
    permission_comment_view
)

from .literals import TEST_COMMENT_TEXT
from .mixins import CommentsTestMixin


class CommentAPITestCase(CommentsTestMixin, DocumentTestMixin, BaseAPITestCase):
    def _request_api_comment_create_view(self):
        return self.post(
            viewname='rest_api:comment-list',
            kwargs={'document_id': self.document.pk}, data={
                'comment': TEST_COMMENT_TEXT
            }
        )

    def test_comment_create_view_no_access(self):
        response = self._request_api_comment_create_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_create_view_with_access(self):
        self.grant_access(permission=permission_comment_create, obj=self.document)
        response = self._request_api_comment_create_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.first()
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(response.data['id'], comment.pk)

    def _request_api_comment_delete_view(self):
        return self.delete(
            viewname='rest_api:comment-detail', kwargs={
                'document_id': self.document.pk,
                'comment_id': self.test_comment.pk
            }
        )

    def test_comment_delete_view_no_access(self):
        self._create_comment()
        response = self._request_api_comment_delete_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.test_comment in Comment.objects.all())

    def test_comment_delete_view_with_access(self):
        self._create_comment()
        self.grant_access(
            permission=permission_comment_delete, obj=self.document
        )
        response = self._request_api_comment_delete_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.test_comment in Comment.objects.all())

    def _request_api_comment_detail_view(self):
        return self.get(
            viewname='rest_api:comment-detail', kwargs={
                'document_id': self.document.pk,
                'comment_id': self.test_comment.pk
            }
        )

    def test_comment_detail_view_no_access(self):
        self._create_comment()
        response = self._request_api_comment_detail_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_comment_detail_view_with_access(self):
        self._create_comment()
        self.grant_access(
            permission=permission_comment_view, obj=self.document
        )
        response = self._request_api_comment_detail_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], self.test_comment.comment)

    def _request_api_comment_list_view(self):
        return self.get(
            viewname='rest_api:comment-list',
            kwargs={'document_id': self.document.pk}
        )

    def test_comment_list_view_no_access(self):
        self._create_comment()
        response = self._request_api_comment_list_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_comment_list_view_with_access(self):
        self._create_comment()
        self.grant_access(
            permission=permission_comment_view, obj=self.document
        )
        response = self._request_api_comment_list_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['comment'], self.test_comment.comment
        )

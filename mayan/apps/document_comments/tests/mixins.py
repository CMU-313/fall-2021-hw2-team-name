from __future__ import unicode_literals

from ..models import Comment

from .literals import TEST_COMMENT_TEXT


class CommentsTestMixin(object):
    def _create_comment(self, user=None):
        self.test_comment = self.document.comments.create(
            comment=TEST_COMMENT_TEXT,
            user=user or self._test_case_user or self.admin_user
        )

    def _request_document_comment_add_view(self):
        response = self.post(
            viewname='comments:comment_add',
            kwargs={'document_id': self.document.pk},
            data={'comment': TEST_COMMENT_TEXT}
        )
        self.test_comment = Comment.objects.filter(
            document=self.document.pk
        ).first()

        return response

    def _request_document_comment_delete_view(self):
        return self.post(
            viewname='comments:comment_delete',
            kwargs={'comment_id': self.test_comment.pk},
        )

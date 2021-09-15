from __future__ import absolute_import, unicode_literals

from rest_framework import generics

from mayan.apps.common.mixins import ExternalObjectMixin
from mayan.apps.documents.models import Document

from .permissions import (
    permission_comment_create, permission_comment_delete,
    permission_comment_view
)
from .serializers import CommentSerializer, WritableCommentSerializer


class APICommentListView(ExternalObjectMixin, generics.ListCreateAPIView):
    """
    get: Returns a list of all the document comments.
    post: Create a new document comment.
    """
    external_object_class = Document
    external_object_pk_url_kwarg = 'document_id'

    def get_document(self):
        return self.get_external_object()

    def get_external_object_permission(self):
        if self.request.method == 'GET':
            return permission_comment_view
        else:
            return permission_comment_create

    def get_queryset(self):
        return self.get_document().comments.all()

    def get_serializer(self, *args, **kwargs):
        if not self.request:
            return None

        return super(APICommentListView, self).get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CommentSerializer
        else:
            return WritableCommentSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(APICommentListView, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'document': self.get_document(),
                }
            )

        return context


class APICommentView(ExternalObjectMixin, generics.RetrieveDestroyAPIView):
    """
    delete: Delete the selected document comment.
    get: Returns the details of the selected document comment.
    """
    external_object_class = Document
    external_object_pk_url_kwarg = 'document_id'
    lookup_url_kwarg = 'comment_id'
    serializer_class = CommentSerializer

    def get_document(self):
        return self.get_external_object()

    def get_external_object_permission(self):
        if self.request.method == 'GET':
            return permission_comment_view
        else:
            return permission_comment_delete

    def get_queryset(self):
        return self.get_document().comments.all()

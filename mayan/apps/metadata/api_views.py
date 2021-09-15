from __future__ import absolute_import, unicode_literals

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import (
    permission_document_type_view, permission_document_type_edit,
)
from mayan.apps.rest_api.mixins import ExternalObjectAPIViewSetMixin
from mayan.apps.rest_api.viewsets import (
    MayanAPIModelViewSet, MayanRetrieveUpdateAPIViewSet,
)

from .models import MetadataType
from .permissions import (
    permission_metadata_add, permission_metadata_remove,
    permission_metadata_edit, permission_metadata_view,
    permission_metadata_type_create, permission_metadata_type_delete,
    permission_metadata_type_edit, permission_metadata_type_view
)
from .serializers import (
    DocumentMetadataAddSerializer,
    DocumentMetadataSerializer,
    MetadataTypeSerializer,
    MetadataTypeDocumentTypeRelationSerializer,
    MetadataTypeDocumentTypeRelationAddRemoveSerializer,
)


class MetadataTypeDocumentTypeRelationAPIViewSet(ExternalObjectAPIViewSetMixin, MayanRetrieveUpdateAPIViewSet):
    external_object_class = MetadataType
    external_object_pk_url_kwarg = 'metadata_type_id'
    lookup_url_kwarg = 'metadata_type_document_type_relation_id'
    object_permission_map = {
        'add': permission_metadata_type_edit,
        'list': permission_document_type_view,
        'partial_update': permission_document_type_edit,
        'remove': permission_metadata_type_edit,
        'retrieve': permission_document_type_view,
        'update': permission_document_type_edit,
    }
    serializer_class = MetadataTypeDocumentTypeRelationSerializer

    def get_external_object_permission(self):
        action = getattr(self, 'action', None)
        if action is None:
            return None
        elif action in ['list', 'retrieve']:
            return permission_metadata_type_view
        else:
            return permission_metadata_type_edit

    def get_queryset(self):
        action = getattr(self, 'action', None)
        if action in ['add', 'remove']:
            # Return metadata types
            return self.get_external_object_queryset()
        else:
            # Return relations
            return self.get_external_object().document_type_relations.all()

    @action(
        detail=False, lookup_url_kwarg='metadata_type_id', methods=('post',),
        serializer_class=MetadataTypeDocumentTypeRelationAddRemoveSerializer,
        url_name='add', url_path='add'
    )
    def add(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.document_type_relations_add(instance=instance)
        headers = self.get_success_headers(data=serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    @action(
        detail=False, lookup_url_kwarg='metadata_type_id', methods=('post',),
        serializer_class=MetadataTypeDocumentTypeRelationAddRemoveSerializer,
        url_name='remove', url_path='remove'
    )
    def remove(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.document_type_relations_remove(instance=instance)
        headers = self.get_success_headers(data=serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )


class MetadataTypeAPIViewSet(MayanAPIModelViewSet):
    lookup_url_kwarg = 'metadata_type_id'
    object_permission_map = {
        'destroy': permission_metadata_type_delete,
        'list': permission_metadata_type_view,
        'partial_update': permission_metadata_type_edit,
        'retrieve': permission_metadata_type_view,
        'update': permission_metadata_type_edit,
    }
    queryset = MetadataType.objects.all()
    serializer_class = MetadataTypeSerializer
    view_permission_map = {
        'create': permission_metadata_type_create
    }


class DocumentMetadataAPIViewSet(ExternalObjectAPIViewSetMixin, MayanAPIModelViewSet):
    external_object_class = Document
    external_object_pk_url_kwarg = 'document_id'
    lookup_url_kwarg = 'document_metadata_id'
    object_permission_map = {
        'list': permission_metadata_view,
        'partial_update': permission_metadata_edit,
        'destroy': permission_metadata_remove,
        'retrieve': permission_metadata_view,
        'update': permission_metadata_edit,
    }

    def get_external_object_permission(self):
        action = getattr(self, 'action', None)
        if action is None:
            return None
        elif action == 'create':
            return permission_metadata_add
        elif action == 'destroy':
            return permission_metadata_remove
        elif action in ['partial_update', 'update']:
            return permission_metadata_edit
        else:
            return permission_metadata_view

    def get_queryset(self):
        return self.get_external_object().metadata.all()

    def get_serializer_class(self):
        action = getattr(self, 'action', None)
        if action is None:
            return None
        if action == 'create':
            return DocumentMetadataAddSerializer
        else:
            return DocumentMetadataSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(DocumentMetadataAPIViewSet, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'document': self.get_external_object(),
                }
            )

        return context

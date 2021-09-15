from __future__ import absolute_import, unicode_literals

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from mayan.apps.common.mixins import ContentTypeViewMixin
from mayan.apps.permissions.serializers import (
    PermissionSerializer, RolePermissionAddRemoveSerializer
)
from mayan.apps.rest_api.mixins import ExternalObjectAPIViewSetMixin
from mayan.apps.rest_api.viewsets import MayanAPIModelViewSet

from .permissions import permission_acl_edit, permission_acl_view
from .serializers import AccessControlListSerializer


class ObjectACLAPIViewSet(ContentTypeViewMixin, ExternalObjectAPIViewSetMixin, MayanAPIModelViewSet):
    content_type_url_kw_args = {
        'app_label': 'app_label',
        'model': 'model_name'
    }
    external_object_pk_url_kwarg = 'object_id'
    lookup_url_kwarg = 'acl_id'
    serializer_class = AccessControlListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.update(
            {
                'object_id': self.external_object.pk,
                'content_type': self.get_content_type(),
            }
        )
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_external_object_permission(self):
        action = getattr(self, 'action', None)
        if action is None:
            return None
        elif action in ['list', 'retrieve', 'permission_list', 'permission_inherited_list']:
            return permission_acl_view
        else:
            return permission_acl_edit

    def get_external_object_queryset(self):
        # Here we get a queryset the object model for which the event
        # will be accessed.
        return self.get_content_type().get_all_objects_for_this_type()

    def get_queryset(self):
        return self.get_external_object().acls.all()

    @action(
        detail=True, lookup_url_kwarg='acl_id', methods=('post',),
        serializer_class=RolePermissionAddRemoveSerializer,
        url_name='permission-add', url_path='permissions/add'
    )
    def permission_add(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.permissions_add(instance=instance)
        headers = self.get_success_headers(data=serializer.data)
        return Response(
            serializer.data, headers=headers, status=status.HTTP_200_OK
        )

    @action(
        detail=True, lookup_url_kwarg='acl_id',
        serializer_class=PermissionSerializer, url_name='permission-list',
        url_path='permissions'
    )
    def permission_list(self, request, *args, **kwargs):
        queryset = self.get_object().permissions.all()
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(
            queryset, many=True, context={'request': request}
        )

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)

    @action(
        detail=True, lookup_url_kwarg='acl_id',
        serializer_class=PermissionSerializer,
        url_name='permission-inherited-list', url_path='permissions/inherited'
    )
    def permission_inherited_list(self, request, *args, **kwargs):
        queryset = self.get_object().get_inherited_permissions()
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(
            queryset, many=True, context={'request': request}
        )

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)

    @action(
        detail=True, lookup_url_kwarg='acl_id',
        methods=('post',), serializer_class=RolePermissionAddRemoveSerializer,
        url_name='permission-remove', url_path='permissions/remove'
    )
    def permission_remove(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.permissions_remove(instance=instance)
        headers = self.get_success_headers(data=serializer.data)
        return Response(
            serializer.data, headers=headers, status=status.HTTP_200_OK
        )

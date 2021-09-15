from __future__ import unicode_literals

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from mayan.apps.rest_api.viewsets import MayanAPIModelViewSet
from mayan.apps.user_management.permissions import permission_group_view
from mayan.apps.user_management.serializers import GroupSerializer

from .classes import PermissionNamespace
from .models import Role
from .permissions import (
    permission_role_create, permission_role_delete, permission_role_edit,
    permission_role_view
)
from .serializers import (
    PermissionNamespaceSerializer, PermissionSerializer, RoleGroupAddRemoveSerializer,
    RolePermissionAddRemoveSerializer, RoleSerializer
)


class PermissionNamespaceAPIViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'name'
    lookup_url_kwarg = 'permission_namespace_name'
    serializer_class = PermissionNamespaceSerializer

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        return PermissionNamespace.get(**filter_kwargs)

    @action(
        detail=True, serializer_class=PermissionSerializer,
        url_name='permission-list', url_path='permissions'
    )
    def permission_list(self, request, *args, **kwargs):
        queryset = self.get_object().permissions
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(
            queryset, many=True, context={'request': request}
        )

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)

    def get_queryset(self):
        return PermissionNamespace.all()


class PermissionAPIViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'pk'
    lookup_url_kwarg = 'permission_name'
    lookup_value_regex = r'[\w\.]+'
    serializer_class = PermissionSerializer

    def get_object(self):
        namespace = PermissionNamespace.get(name=self.kwargs['permission_namespace_name'])
        permissions = namespace.get_permissions()
        return permissions.get(self.kwargs['permission_name'])


class RoleAPIViewSet(MayanAPIModelViewSet):
    lookup_url_kwarg = 'role_id'
    object_permission_map = {
        'destroy': permission_role_delete,
        'group_add': permission_role_edit,
        'group_list': permission_role_view,
        'group_remove': permission_role_edit,
        'list': permission_role_view,
        'partial_update': permission_role_edit,
        'permission_add': permission_role_edit,
        'permission_list': permission_role_view,
        'permission_remove': permission_role_edit,
        'retrieve': permission_role_view,
        'update': permission_role_edit,
    }
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    view_permission_map = {
        'create': permission_role_create
    }

    @action(
        detail=True, lookup_url_kwarg='role_id', methods=('post',),
        serializer_class=RoleGroupAddRemoveSerializer,
        url_name='group-add', url_path='groups/add'
    )
    def group_add(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.groups_add(instance=instance)
        headers = self.get_success_headers(data=serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    @action(
        detail=True, lookup_url_kwarg='role_id',
        serializer_class=GroupSerializer, url_name='group-list',
        url_path='groups'
    )
    def group_list(self, request, *args, **kwargs):
        queryset = self.get_object().get_groups(
            permission=permission_group_view, user=self.request.user
        )
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(
            queryset, many=True, context={'request': request}
        )

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)

    @action(
        detail=True, lookup_url_kwarg='role_id',
        methods=('post',), serializer_class=RoleGroupAddRemoveSerializer,
        url_name='group-remove', url_path='groups/remove'
    )
    def group_remove(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.groups_remove(instance=instance)
        headers = self.get_success_headers(data=serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    @action(
        detail=True, lookup_url_kwarg='role_id', methods=('post',),
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
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    @action(
        detail=True, lookup_url_kwarg='role_id',
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
        detail=True, lookup_url_kwarg='role_id',
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
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

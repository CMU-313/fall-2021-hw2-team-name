from __future__ import unicode_literals

from django.contrib.auth.models import Group

from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mayan.apps.rest_api.viewsets import MayanAPIModelViewSet

from .permissions import (
    permission_group_create, permission_group_delete, permission_group_edit,
    permission_group_view, permission_user_create, permission_user_delete,
    permission_user_edit, permission_user_view
)
from .serializers import (
    CurrentUserSerializer, GroupUserAddRemoveSerializer, GroupSerializer,
    UserGroupAddRemoveSerializer, UserSerializer
)
from .querysets import get_user_queryset


class CurrentUserAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CurrentUserSerializer

    def get_object(self):
        return self.request.user


class GroupAPIViewSet(MayanAPIModelViewSet):
    lookup_url_kwarg = 'group_id'
    object_permission_map = {
        'destroy': permission_group_delete,
        'list': permission_group_view,
        'partial_update': permission_group_edit,
        'retrieve': permission_group_view,
        'update': permission_group_edit,
        'user_add': permission_group_edit,
        'user_list': permission_group_view,
        'user_remove': permission_group_edit
    }
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    view_permission_map = {
        'create': permission_group_create
    }

    @action(
        detail=True, lookup_url_kwarg='group_id', methods=('post',),
        serializer_class=GroupUserAddRemoveSerializer,
        url_name='user-add', url_path='users/add'
    )
    def user_add(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.users_add(instance=instance)
        headers = self.get_success_headers(data=serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    @action(
        detail=True, lookup_url_kwarg='group_id',
        serializer_class=UserSerializer, url_name='user-list',
        url_path='users'
    )
    def user_list(self, request, *args, **kwargs):
        queryset = self.get_object().get_users(_user=self.request.user)
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(
            queryset, many=True, context={'request': request}
        )

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)

    @action(
        detail=True, lookup_url_kwarg='group_id',
        methods=('post',), serializer_class=GroupUserAddRemoveSerializer,
        url_name='user-remove', url_path='users/remove'
    )
    def user_remove(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.users_remove(instance=instance)
        headers = self.get_success_headers(data=serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )


class UserAPIViewSet(MayanAPIModelViewSet):
    lookup_url_kwarg = 'user_id'
    object_permission_map = {
        'destroy': permission_user_delete,
        'group_add': permission_user_edit,
        'group_list': permission_user_view,
        'group_remove': permission_user_edit,
        'list': permission_user_view,
        'partial_update': permission_user_edit,
        'retrieve': permission_user_view,
        'update': permission_user_edit,
    }
    queryset = get_user_queryset()
    serializer_class = UserSerializer
    view_permission_map = {
        'create': permission_user_create
    }

    @action(
        detail=True, lookup_url_kwarg='user_id', methods=('post',),
        serializer_class=UserGroupAddRemoveSerializer,
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
        detail=True, lookup_url_kwarg='user_id',
        serializer_class=GroupSerializer, url_name='group-list',
        url_path='groups'
    )
    def group_list(self, request, *args, **kwargs):
        queryset = self.get_object().get_groups(_user=self.request.user)
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(
            queryset, many=True, context={'request': request}
        )

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)

    @action(
        detail=True, lookup_url_kwarg='user_id',
        methods=('post',), serializer_class=UserGroupAddRemoveSerializer,
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

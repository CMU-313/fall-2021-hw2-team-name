from __future__ import absolute_import, unicode_literals

from rest_framework import generics

from mayan.apps.rest_api.filters import MayanObjectPermissionsFilter
from mayan.apps.rest_api.permissions import MayanPermission


class ListAPIView(generics.ListAPIView):
    """
    requires:
        object_permission = {'GET': ...}
    """
    filter_backends = (MayanObjectPermissionsFilter,)


class ListCreateAPIView(generics.ListCreateAPIView):
    """
    requires:
        object_permission = {'GET': ...}
        view_permission = {'POST': ...}
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    permission_classes = (MayanPermission,)


class RetrieveDestroyAPIView(generics.RetrieveDestroyAPIView):
    """
    requires:
        object_permission = {
            'DELETE': ...,
            'GET': ...,
        }
    """
    filter_backends = (MayanObjectPermissionsFilter,)


class RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    requires:
        object_permission = {
            'DELETE': ...,
            'GET': ...,
            'PATCH': ...,
            'PUT': ...
        }
    """
    filter_backends = (MayanObjectPermissionsFilter,)

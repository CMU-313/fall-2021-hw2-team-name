from __future__ import absolute_import, unicode_literals

from mayan.apps.rest_api.viewsets import MayanAPIModelViewSet

from .models import Key
from .permissions import (
    permission_key_delete, permission_key_upload, permission_key_view
)
from .serializers import KeySerializer


class KeyAPIViewSet(MayanAPIModelViewSet):
    lookup_url_kwarg = 'key_id'
    object_permission_map = {
        'destroy': permission_key_delete,
        'list': permission_key_view,
        'retrieve': permission_key_view,
    }
    queryset = Key.objects.all()
    serializer_class = KeySerializer
    view_permission_map = {
        'create': permission_key_upload
    }

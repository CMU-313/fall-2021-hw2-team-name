from __future__ import absolute_import, unicode_literals

from mayan.apps.rest_api.viewsets import MayanAPIModelViewSet

from .models import Message
from .permissions import (
    permission_message_create, permission_message_delete,
    permission_message_edit, permission_message_view
)
from .serializers import MessageSerializer


class MessageAPIViewSet(MayanAPIModelViewSet):
    """
    create:
    Create a new message.

    delete:
    Delete the given message.

    edit:
    Edit the given message.

    list:
    Return a list of all the messages.

    retrieve:
    Return the given message details.
    """
    lookup_url_kwarg = 'message_id'
    object_permission_map = {
        'destroy': permission_message_delete,
        'list': permission_message_view,
        'partial_update': permission_message_edit,
        'retrieve': permission_message_view,
        'update': permission_message_edit,
    }
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    view_permission_map = {
        'create': permission_message_create
    }

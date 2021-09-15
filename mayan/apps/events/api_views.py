from __future__ import absolute_import, unicode_literals

from actstream.models import any_stream
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from mayan.apps.common.mixins import ContentTypeViewMixin
from mayan.apps.rest_api.mixins import ExternalObjectAPIViewSetMixin
from mayan.apps.rest_api.viewsets import MayanAPIReadOnlyModelViewSet

from .classes import EventTypeNamespace
from .models import Notification
from .permissions import permission_events_view
from .serializers import (
    EventSerializer, EventTypeNamespaceSerializer, EventTypeSerializer,
    NotificationSerializer
)


class EventTypeNamespaceAPIViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'name'
    lookup_url_kwarg = 'event_type_namespace_name'
    serializer_class = EventTypeNamespaceSerializer

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        return EventTypeNamespace.get(**filter_kwargs)

    @action(
        detail=True, serializer_class=EventTypeSerializer,
        url_name='event_type-list', url_path='event_types'
    )
    def event_type_list(self, request, *args, **kwargs):
        queryset = self.get_object().event_types
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(
            queryset, many=True, context={'request': request}
        )

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)

    def get_queryset(self):
        return EventTypeNamespace.all()


class EventTypeAPIViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'id'
    lookup_url_kwarg = 'event_type_id'
    lookup_value_regex = r'[\w\.]+'
    serializer_class = EventTypeSerializer

    def get_object(self):
        namespace = EventTypeNamespace.get(name=self.kwargs['event_type_namespace_name'])
        event_types = namespace.get_event_types()
        return event_types.get(self.kwargs['event_type_id'])


class NotificationAPIViewSet(MayanAPIReadOnlyModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        query_parameter = 'read'
        parameter_read = self.request.GET.get(query_parameter)

        if self.request.user.is_authenticated:
            queryset = Notification.objects.filter(user=self.request.user)
        else:
            queryset = Notification.objects.none()

        if parameter_read == 'True':
            queryset = queryset.filter(read=True)
        elif parameter_read == 'False':
            queryset = queryset.filter(read=False)

        return queryset


class ObjectEventAPIViewSet(ContentTypeViewMixin, ExternalObjectAPIViewSetMixin, MayanAPIReadOnlyModelViewSet):
    content_type_url_kw_args = {
        'app_label': 'app_label',
        'model': 'model_name'
    }

    external_object_permission = permission_events_view
    external_object_pk_url_kwarg = 'object_id'
    serializer_class = EventSerializer

    def get_external_object_queryset(self):
        # Here we get a queryset the object model for which the event
        # will be accessed.
        return self.get_content_type().get_all_objects_for_this_type()

    def get_queryset(self):
        obj = self.get_external_object()

        return any_stream(obj)

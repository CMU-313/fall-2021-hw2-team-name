from __future__ import unicode_literals

from django.utils.six import string_types

from actstream.models import Action
from rest_framework import serializers

from mayan.apps.common.serializers import ContentTypeSerializer
from mayan.apps.rest_api.fields import DynamicSerializerField
from mayan.apps.rest_api.relations import MultiKwargHyperlinkedIdentityField
from mayan.apps.user_management.serializers import UserSerializer

from .classes import EventType
from .models import Notification, StoredEventType


class EventTypeNamespaceSerializer(serializers.Serializer):
    label = serializers.CharField()
    name = serializers.CharField()
    event_type_list_url = serializers.HyperlinkedIdentityField(
        lookup_field='name',
        lookup_url_kwarg='event_type_namespace_name',
        view_name='rest_api:event_type_namespace-event_type-list'
    )
    url = serializers.HyperlinkedIdentityField(
        lookup_field='name',
        lookup_url_kwarg='event_type_namespace_name',
        view_name='rest_api:event_type_namespace-detail'
    )


class EventTypeSerializer(serializers.Serializer):
    label = serializers.CharField()
    name = serializers.CharField()
    id = serializers.CharField()
    event_type_namespace = EventTypeNamespaceSerializer(source='namespace')
    url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'namespace.name', 'lookup_url_kwarg': 'event_type_namespace_name',
            },
            {
                'lookup_field': 'id', 'lookup_url_kwarg': 'event_type_id',
            }
        ),
        view_name='rest_api:event_type-detail'
    )

    def to_representation(self, instance):
        if isinstance(instance, EventType):
            return super(EventTypeSerializer, self).to_representation(
                instance
            )
        elif isinstance(instance, StoredEventType):
            return super(EventTypeSerializer, self).to_representation(
                instance.get_class()
            )
        elif isinstance(instance, string_types):
            return super(EventTypeSerializer, self).to_representation(
                EventType.get(name=instance)
            )


class EventSerializer(serializers.ModelSerializer):
    actor = DynamicSerializerField(read_only=True)
    target = DynamicSerializerField(read_only=True)
    actor_content_type = ContentTypeSerializer(read_only=True)
    target_content_type = ContentTypeSerializer(read_only=True)
    verb = EventTypeSerializer(read_only=True)

    class Meta:
        exclude = (
            'action_object_content_type', 'action_object_object_id'
        )
        model = Action


class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    action = EventSerializer(read_only=True)

    class Meta:
        fields = ('action', 'read', 'user')
        model = Notification

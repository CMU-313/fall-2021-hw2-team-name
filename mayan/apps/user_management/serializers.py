from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from mayan.apps.rest_api.mixins import ExternalObjectListSerializerMixin

from .permissions import permission_group_edit, permission_user_edit
from .querysets import get_user_queryset


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    user_add_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='group_id', view_name='rest_api:group-user-add'
    )

    user_list_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='group_id', view_name='rest_api:group-user-list'
    )

    user_remove_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='group_id', view_name='rest_api:group-user-remove'
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'group_id',
                'view_name': 'rest_api:group-detail'
            }
        }
        fields = (
            'id', 'name', 'url', 'user_add_url', 'user_list_url',
            'user_remove_url'
        )
        model = Group


class GroupUserAddRemoveSerializer(ExternalObjectListSerializerMixin, serializers.Serializer):
    user_id = serializers.CharField(
        help_text=_(
            'Primary key of the user that will be added or removed.'
        ), required=False, write_only=True
    )
    user_id_list = serializers.CharField(
        help_text=_(
            'Comma separated list of user primary keys that will be added or '
            'removed.'
        ), required=False, write_only=True
    )

    class Meta:
        external_object_list_queryset = get_user_queryset()
        external_object_list_permission = permission_user_edit
        external_object_list_pk_field = 'user_id'
        external_object_list_pk_list_field = 'user_id_list'

    def users_add(self, instance):
        instance.users_add(
            users=self.get_external_object_list(),
            _user=self.context['request'].user
        )

    def users_remove(self, instance):
        instance.users_remove(
            users=self.get_external_object_list(),
            _user=self.context['request'].user
        )


class UserGroupAddRemoveSerializer(ExternalObjectListSerializerMixin, serializers.Serializer):
    group_id = serializers.CharField(
        help_text=_(
            'Primary key of the group that will be added or removed.'
        ), required=False, write_only=True
    )
    group_id_list = serializers.CharField(
        help_text=_(
            'Comma separated list of group primary keys that will be added or '
            'removed.'
        ), required=False, write_only=True
    )

    class Meta:
        external_object_list_queryset = Group.objects.all()
        external_object_list_permission = permission_group_edit
        external_object_list_pk_field = 'group_id'
        external_object_list_pk_list_field = 'group_id_list'

    def groups_add(self, instance):
        instance.groups_add(
            groups=self.get_external_object_list(),
            _user=self.context['request'].user
        )

    def groups_remove(self, instance):
        instance.groups_remove(
            groups=self.get_external_object_list(),
            _user=self.context['request'].user
        )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    group_add_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='user_id', view_name='rest_api:user-group-add'
    )
    group_list_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='user_id', view_name='rest_api:user-group-list'
    )
    group_remove_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='user_id', view_name='rest_api:user-group-remove'
    )
    password = serializers.CharField(
        required=False, style={'input_type': 'password'}, write_only=True
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'user_id',
                'view_name': 'rest_api:user-detail'
            }
        }
        fields = (
            'first_name', 'date_joined', 'email', 'group_add_url',
            'group_list_url', 'group_remove_url', 'id', 'is_active',
            'last_login', 'last_name', 'password', 'url', 'username'
        )
        model = get_user_model()
        read_only_fields = ('is_active', 'last_login', 'date_joined')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = super(UserSerializer, self).create(validated_data)

        if password:
            instance.set_password(password)
            instance.save()

        return instance

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            validated_data.pop('password')

        instance = super(UserSerializer, self).update(instance, validated_data)

        return instance

    def validate(self, data):
        if 'password' in data:
            validate_password(data['password'], self.instance)

        return data


class CurrentUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        # Remove some fields that don't apply to the current user
        _field_list = (
            'group_add_url', 'group_list_url', 'group_remove_url', 'url'
        )
        fields = [
            field for field in UserSerializer.Meta.fields if field not in _field_list
        ]

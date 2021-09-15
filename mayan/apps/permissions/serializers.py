from __future__ import unicode_literals

from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from mayan.apps.rest_api.mixins import ExternalObjectListSerializerMixin
from mayan.apps.rest_api.relations import MultiKwargHyperlinkedIdentityField
from mayan.apps.user_management.permissions import permission_group_edit

from .classes import Permission
from .models import Role, StoredPermission


class PermissionNamespaceSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    label = serializers.CharField(read_only=True)
    permission_list_url = serializers.HyperlinkedIdentityField(
        lookup_field='name',
        lookup_url_kwarg='permission_namespace_name',
        view_name='rest_api:permission_namespace-permission-list'
    )
    url = serializers.HyperlinkedIdentityField(
        lookup_field='name',
        lookup_url_kwarg='permission_namespace_name',
        view_name='rest_api:permission_namespace-detail'
    )


class PermissionSerializer(serializers.Serializer):
    permission_namespace = PermissionNamespaceSerializer(source='namespace')
    pk = serializers.CharField(read_only=True)
    label = serializers.CharField(read_only=True)
    url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'namespace.name', 'lookup_url_kwarg': 'permission_namespace_name',
            },
            {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'permission_name',
            }
        ),
        view_name='rest_api:permission-detail'
    )

    def to_representation(self, instance):
        if isinstance(instance, StoredPermission):
            return super(PermissionSerializer, self).to_representation(
                instance.volatile_permission
            )
        else:
            return super(PermissionSerializer, self).to_representation(
                instance
            )


class RoleGroupAddRemoveSerializer(ExternalObjectListSerializerMixin, serializers.Serializer):
    group_id_list = serializers.CharField(
        help_text=_(
            'Comma separated list of group primary keys that will be added or '
            'removed.'
        ), required=False, write_only=True
    )

    class Meta:
        external_object_list_model = Group
        external_object_list_permission = permission_group_edit
        external_object_list_pk_list_field = 'group_id_list'

    def groups_add(self, instance):
        instance.groups_add(
            queryset=self.get_external_object_list(),
            _user=self.context['request'].user
        )

    def groups_remove(self, instance):
        instance.groups_remove(
            queryset=self.get_external_object_list(),
            _user=self.context['request'].user
        )


class RolePermissionAddRemoveSerializer(ExternalObjectListSerializerMixin, serializers.Serializer):
    permission_id_list = serializers.CharField(
        help_text=_(
            'Comma separated list of permission primary keys that will be added or '
            'removed.'
        ), label=_('Permission ID list'), required=False, write_only=True
    )

    class Meta:
        external_object_list_model = Permission
        external_object_list_pk_list_field = 'permission_id_list'
        external_object_list_pk_type = None

    def filter_queryset(self, id_list, queryset):
        result = []
        for pk in id_list:
            try:
                result.append(Permission.get(pk=pk))
            except KeyError:
                raise ValidationError(
                    {
                        'permission_id_list': [
                            'Permission "{}" not found.'.format(pk)
                        ]
                    }, code='invalid'
                )

        return result

    def get_external_object_list_queryset(self):
        return Permission.all()

    def permissions_add(self, instance):
        instance.permissions_add(
            queryset=self.get_external_object_list(),
            _user=self.context['request'].user
        )

    def permissions_remove(self, instance):
        instance.permissions_remove(
            queryset=self.get_external_object_list(),
            _user=self.context['request'].user
        )


class RoleSerializer(serializers.HyperlinkedModelSerializer):
    group_add_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='role_id', view_name='rest_api:role-group-add'
    )
    group_list_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='role_id', view_name='rest_api:role-group-list'
    )
    group_remove_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='role_id', view_name='rest_api:role-group-remove'
    )
    permission_add_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='role_id', view_name='rest_api:role-permission-add'
    )
    permission_list_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='role_id', view_name='rest_api:role-permission-list'
    )
    permission_remove_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='role_id', view_name='rest_api:role-permission-remove'
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'role_id',
                'view_name': 'rest_api:role-detail'
            }
        }
        fields = (
            'id', 'label', 'url', 'group_add_url', 'group_list_url',
            'group_remove_url', 'permission_add_url', 'permission_list_url',
            'permission_remove_url'
        )
        model = Role

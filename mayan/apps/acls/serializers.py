from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from mayan.apps.common.serializers import ContentTypeSerializer
from mayan.apps.permissions.models import Role
from mayan.apps.permissions.permissions import permission_role_edit
from mayan.apps.permissions.serializers import RoleSerializer
from mayan.apps.rest_api.mixins import ExternalObjectSerializerMixin
from mayan.apps.rest_api.relations import MultiKwargHyperlinkedIdentityField

from .models import AccessControlList


class AccessControlListSerializer(ExternalObjectSerializerMixin, serializers.ModelSerializer):
    content_type = ContentTypeSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    permission_add_url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'content_type__app_label', 'lookup_url_kwarg': 'app_label',
            },
            {
                'lookup_field': 'content_type__model', 'lookup_url_kwarg': 'model_name',
            },
            {
                'lookup_field': 'object_id', 'lookup_url_kwarg': 'object_id',
            },
            {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'acl_id',
            }
        ),
        view_name='rest_api:object-acl-permission-add'
    )
    permission_list_url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'content_type__app_label', 'lookup_url_kwarg': 'app_label',
            },
            {
                'lookup_field': 'content_type__model', 'lookup_url_kwarg': 'model_name',
            },
            {
                'lookup_field': 'object_id', 'lookup_url_kwarg': 'object_id',
            },
            {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'acl_id',
            }
        ),
        view_name='rest_api:object-acl-permission-list'
    )
    permission_list_inherited_url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'content_type__app_label', 'lookup_url_kwarg': 'app_label',
            },
            {
                'lookup_field': 'content_type__model', 'lookup_url_kwarg': 'model_name',
            },
            {
                'lookup_field': 'object_id', 'lookup_url_kwarg': 'object_id',
            },
            {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'acl_id',
            }
        ),
        view_name='rest_api:object-acl-permission-inherited-list'
    )
    permission_remove_url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'content_type__app_label', 'lookup_url_kwarg': 'app_label',
            },
            {
                'lookup_field': 'content_type__model', 'lookup_url_kwarg': 'model_name',
            },
            {
                'lookup_field': 'object_id', 'lookup_url_kwarg': 'object_id',
            },
            {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'acl_id',
            }
        ),
        view_name='rest_api:object-acl-permission-remove'
    )
    role_id = serializers.CharField(
        label=_('Role ID'),
        help_text=_(
            'Primary key of the role of the ACL that will be created or edited.'
        ), required=False, write_only=True
    )
    url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'content_type__app_label', 'lookup_url_kwarg': 'app_label',
            },
            {
                'lookup_field': 'content_type__model', 'lookup_url_kwarg': 'model_name',
            },
            {
                'lookup_field': 'object_id', 'lookup_url_kwarg': 'object_id',
            },
            {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'acl_id',
            }
        ),
        view_name='rest_api:object-acl-detail'
    )

    class Meta:
        external_object_model = Role
        external_object_pk_field = 'role_id'
        external_object_permission = permission_role_edit
        fields = (
            'content_type', 'id', 'object_id', 'permission_add_url',
            'permission_list_url', 'permission_list_inherited_url',
            'permission_remove_url', 'role', 'role_id',
            'url'
        )
        model = AccessControlList
        read_only_fields = ('object_id',)

    def create(self, validated_data):
        role = self.get_external_object()

        if role:
            validated_data['role'] = role

        return super(AccessControlListSerializer, self).create(
            validated_data=validated_data
        )

    def update(self, instance, validated_data):
        role = self.get_external_object()

        if role:
            validated_data['role'] = role

        return super(AccessControlListSerializer, self).update(
            instance=instance, validated_data=validated_data
        )

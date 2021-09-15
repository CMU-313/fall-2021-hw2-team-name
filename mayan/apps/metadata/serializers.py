from __future__ import unicode_literals

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from mayan.apps.documents.models import DocumentType
from mayan.apps.documents.permissions import permission_document_type_edit
from mayan.apps.documents.serializers import (
    DocumentSerializer, DocumentTypeSerializer
)
from mayan.apps.rest_api.mixins import ExternalObjectListSerializerMixin
from mayan.apps.rest_api.relations import (
    FilteredPrimaryKeyRelatedField, MultiKwargHyperlinkedIdentityField
)

from .models import DocumentMetadata, DocumentTypeMetadataType, MetadataType
from .permissions import permission_metadata_add


class MetadataTypeSerializer(serializers.HyperlinkedModelSerializer):
    document_type_relation_add_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='metadata_type_id', view_name='rest_api:metadata_type-document_type_relation-add'
    )
    document_type_relation_list_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='metadata_type_id', view_name='rest_api:metadata_type-document_type_relation-list'
    )
    document_type_relation_remove_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='metadata_type_id', view_name='rest_api:metadata_type-document_type_relation-remove'
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'metadata_type_id',
                'view_name': 'rest_api:metadata_type-detail'
            },
        }
        fields = (
            'default', 'document_type_relation_add_url', 'document_type_relation_list_url',
            'document_type_relation_remove_url', 'id', 'label', 'lookup', 'name',
            'parser', 'url', 'validation'
        )
        model = MetadataType


class MetadataTypeDocumentTypeRelationSerializer(serializers.HyperlinkedModelSerializer):
    document_type = DocumentTypeSerializer(read_only=True)
    url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'metadata_type_id',
                'lookup_url_kwarg': 'metadata_type_id',
            },
            {
                'lookup_field': 'pk',
                'lookup_url_kwarg': 'metadata_type_document_type_relation_id',
            }
        ),
        view_name='rest_api:metadata_type-document_type_relation-detail'
    )

    class Meta:
        fields = ('document_type', 'id', 'required', 'url')
        model = DocumentTypeMetadataType


class MetadataTypeDocumentTypeRelationAddRemoveSerializer(ExternalObjectListSerializerMixin, serializers.Serializer):
    document_type_id_list = serializers.CharField(
        help_text=_(
            'Comma separated list of document type primary keys that will be '
            'added or removed.'
        ), label=_('Document Type ID list'), required=False, write_only=True
    )
    required = serializers.BooleanField(
        label=_('Required'), required=False, write_only=True
    )

    class Meta:
        external_object_list_model = DocumentType
        external_object_list_permission = permission_document_type_edit
        external_object_list_pk_list_field = 'document_type_id_list'

    def document_type_relations_add(self, instance):
        instance.document_types_add(
            queryset=self.get_external_object_list(),
            required=self.validated_data['required'],
            _user=self.context['request'].user
        )

    def document_type_relations_remove(self, instance):
        instance.document_types_remove(
            queryset=self.get_external_object_list(),
            _user=self.context['request'].user
        )


class DocumentMetadataSerializer(serializers.HyperlinkedModelSerializer):
    document = DocumentSerializer(read_only=True)
    metadata_type = MetadataTypeSerializer(read_only=True)
    url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'document_id',
                'lookup_url_kwarg': 'document_id',
            },
            {
                'lookup_field': 'pk',
                'lookup_url_kwarg': 'document_metadata_id',
            }
        ),
        view_name='rest_api:document-metadata-detail'
    )

    class Meta:
        fields = ('document', 'id', 'metadata_type', 'url', 'value')
        model = DocumentMetadata


class DocumentMetadataAddSerializer(DocumentMetadataSerializer):
    metadata_type = FilteredPrimaryKeyRelatedField(
        source_model=MetadataType, source_permission=permission_metadata_add,
        write_only=True
    )

    class Meta(DocumentMetadataSerializer.Meta):
        read_only_fields = ('document',)

    def create(self, validated_data):
        validated_data['document'] = self.context['document']

        return super(DocumentMetadataAddSerializer, self).create(
            validated_data=validated_data
        )

    def validate(self, attrs):
        attrs['document'] = self.context['document']

        instance = DocumentMetadata(**attrs)

        try:
            instance.full_clean()
        except DjangoValidationError as exception:
            raise ValidationError(
                {
                    api_settings.NON_FIELD_ERRORS_KEY: exception.messages
                }, code='invalid'
            )

        return attrs

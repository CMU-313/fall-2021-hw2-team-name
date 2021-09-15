from __future__ import unicode_literals

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from mayan.apps.documents.models import DocumentType
from mayan.apps.documents.serializers import DocumentTypeSerializer
from mayan.apps.rest_api.relations import (
    FilteredPrimaryKeyRelatedField, MultiKwargHyperlinkedIdentityField
)
from mayan.apps.user_management.serializers import UserSerializer

from .models import (
    Workflow, WorkflowInstance, WorkflowInstanceLogEntry, WorkflowState,
    WorkflowTransition
)
from .permissions import permission_workflow_edit

class WorkflowSerializer(serializers.HyperlinkedModelSerializer):
    #document_types_url = serializers.HyperlinkedIdentityField(
    #    view_name='rest_api:workflow-document-type-list'
    #)
    #image_url = serializers.SerializerMethodField()
    state_list_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='workflow_id',
        view_name='rest_api:workflow-state-list'
    )
    transition_list_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='workflow_id',
        view_name='rest_api:workflow-transition-list'
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'workflow_id',
                'view_name': 'rest_api:workflow-detail'
            },
        }
        fields = (
            #'document_types_url', 'image_url',
            'id', 'internal_name', 'label', 'state_list_url',
            'transition_list_url', 'url'
        )
        model = Workflow


class WorkflowStateSerializer(serializers.HyperlinkedModelSerializer):
    workflow = WorkflowSerializer(read_only=True)
    url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'workflow_id',
                'lookup_url_kwarg': 'workflow_id',
            },
            {
                'lookup_field': 'pk',
                'lookup_url_kwarg': 'workflow_state_id',
            }
        ),
        view_name='rest_api:workflow-state-detail'
    )

    class Meta:
        fields = (
            'completion', 'id', 'initial', 'label', 'url', 'workflow'
        )
        model = WorkflowState

    def create(self, validated_data):
        validated_data['workflow'] = self.context['workflow']
        return super(WorkflowStateSerializer, self).create(validated_data)


class WorkflowTransitionSerializer(serializers.HyperlinkedModelSerializer):
    destination_state = WorkflowStateSerializer(read_only=True)
    origin_state = WorkflowStateSerializer(read_only=True)
    workflow = WorkflowSerializer(read_only=True)
    url = MultiKwargHyperlinkedIdentityField(
        view_kwargs=(
            {
                'lookup_field': 'workflow_id',
                'lookup_url_kwarg': 'workflow_id',
            },
            {
                'lookup_field': 'pk',
                'lookup_url_kwarg': 'workflow_transition_id',
            }
        ),
        view_name='rest_api:workflow-transition-detail'
    )

    class Meta:
        fields = (
            'destination_state', 'id', 'label', 'origin_state', 'url',
            'workflow',
        )
        model = WorkflowTransition


class WorkflowTransitionWritableSerializer(WorkflowTransitionSerializer):
    destination_state = FilteredPrimaryKeyRelatedField(
        label=_('Destination state'),
        source_permission=permission_workflow_edit,
        write_only=True
    )
    origin_state = FilteredPrimaryKeyRelatedField(
        label=_('Source state'),
        source_permission=permission_workflow_edit,
        write_only=True
    )

    def create(self, validated_data):
        validated_data['workflow'] = self.context['workflow']
        return super(WorkflowTransitionWritableSerializer, self).create(
            validated_data=validated_data
        )

    def get_destination_state_queryset(self):
        return self.context['workflow'].states.all()

    def get_origin_state_queryset(self):
        return self.context['workflow'].states.all()

    def update(self, instance, validated_data):
        return super(WorkflowTransitionWritableSerializer, self).update(
            instance=instance, validated_data=validated_data
        )

    """
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
    """




"""
class NewWorkflowDocumentTypeSerializer(serializers.Serializer):
    document_type_pk = serializers.IntegerField(
        help_text=_('Primary key of the document type to be added.')
    )

    def create(self, validated_data):
        document_type = DocumentType.objects.get(
            pk=validated_data['document_type_pk']
        )
        self.context['workflow'].document_types.add(document_type)

        return validated_data


class WorkflowDocumentTypeSerializer(DocumentTypeSerializer):
    workflow_document_type_url = serializers.SerializerMethodField(
        help_text=_(
            'API URL pointing to a document type in relation to the '
            'workflow to which it is attached. This URL is different than '
            'the canonical document type URL.'
        )
    )

    class Meta(DocumentTypeSerializer.Meta):
        fields = DocumentTypeSerializer.Meta.fields + (
            'workflow_document_type_url',
        )
        read_only_fields = DocumentTypeSerializer.Meta.fields

    def get_workflow_document_type_url(self, instance):
        return reverse(
            viewname='rest_api:workflow-document-type-detail', kwargs={
                'workflow_pk': self.context['workflow'].pk, 'document_type_pk': instance.pk
            }, request=self.context['request'], format=self.context['format']
        )


class WorkflowInstanceLogEntrySerializer(serializers.ModelSerializer):
    document_workflow_url = serializers.SerializerMethodField()
    transition = WorkflowTransitionSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        fields = (
            'comment', 'datetime', 'document_workflow_url', 'transition',
            'user'
        )
        model = WorkflowInstanceLogEntry

    def get_document_workflow_url(self, instance):
        return reverse(
            viewname='rest_api:workflowinstance-detail', kwargs={
                'document_pk': instance.workflow_instance.document.pk,
                'transition_pk': instance.workflow_instance.pk
            }, request=self.context['request'], format=self.context['format']
        )


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    current_state = WorkflowStateSerializer(
        read_only=True, source='get_current_state'
    )
    document_workflow_url = serializers.SerializerMethodField(
        help_text=_(
            'API URL pointing to a workflow in relation to the '
            'document to which it is attached. This URL is different than '
            'the canonical workflow URL.'
        )
    )
    last_log_entry = WorkflowInstanceLogEntrySerializer(
        read_only=True, source='get_last_log_entry'
    )
    log_entries_url = serializers.SerializerMethodField(
        help_text=_('A link to the entire history of this workflow.')
    )
    transition_choices = WorkflowTransitionSerializer(
        many=True, read_only=True, source='get_transition_choices'
    )
    workflow = WorkflowSerializer(read_only=True)

    class Meta:
        fields = (
            'current_state', 'document_workflow_url', 'last_log_entry',
            'log_entries_url', 'transition_choices', 'workflow',
        )
        model = WorkflowInstance

    def get_document_workflow_url(self, instance):
        return reverse(
            viewname='rest_api:workflowinstance-detail', kwargs={
                'document_pk': instance.document.pk, 'transition_pk': instance.pk,
            }, request=self.context['request'], format=self.context['format']
        )

    def get_log_entries_url(self, instance):
        return reverse(
            viewname='rest_api:workflowinstancelogentry-list', kwargs={
                'document_pk': instance.document.pk, 'workflow_pk': instance.pk,
            }, request=self.context['request'], format=self.context['format']
        )


class WritableWorkflowSerializer(serializers.ModelSerializer):
    document_types_pk_list = serializers.CharField(
        help_text=_(
            'Comma separated list of document type primary keys to which this '
            'workflow will be attached.'
        ), required=False
    )

    class Meta:
        extra_kwargs = {
            'url': {'view_name': 'rest_api:workflow-detail'},
        }
        fields = (
            'document_types_pk_list', 'label', 'id', 'url',
        )
        model = Workflow

    def _add_document_types(self, document_types_pk_list, instance):
        instance.document_types.add(
            *DocumentType.objects.filter(
                pk__in=document_types_pk_list.split(',')
            )
        )

    def create(self, validated_data):
        document_types_pk_list = validated_data.pop(
            'document_types_pk_list', ''
        )

        instance = super(WritableWorkflowSerializer, self).create(
            validated_data
        )

        if document_types_pk_list:
            self._add_document_types(
                document_types_pk_list=document_types_pk_list,
                instance=instance
            )

        return instance

    def update(self, instance, validated_data):
        document_types_pk_list = validated_data.pop(
            'document_types_pk_list', ''
        )

        instance = super(WritableWorkflowSerializer, self).update(
            instance, validated_data
        )

        if document_types_pk_list:
            instance.documents.clear()
            self._add_documents(
                document_types_pk_list=document_types_pk_list,
                instance=instance
            )

        return instance


class WritableWorkflowInstanceLogEntrySerializer(serializers.ModelSerializer):
    document_workflow_url = serializers.SerializerMethodField()
    transition_pk = serializers.IntegerField(
        help_text=_('Primary key of the transition to be added.'),
        write_only=True
    )
    transition = WorkflowTransitionSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        fields = (
            'comment', 'datetime', 'document_workflow_url', 'transition',
            'transition_pk', 'user'
        )
        model = WorkflowInstanceLogEntry

    def get_document_workflow_url(self, instance):
        return reverse(
            viewname='rest_api:workflowinstance-detail', kwargs={
                'document_pk': instance.workflow_instance.document.pk,
                'workflow_pk': instance.workflow_instance.pk,
            }, request=self.context['request'], format=self.context['format']
        )

    def validate(self, attrs):
        attrs['user'] = self.context['request'].user
        attrs['workflow_instance'] = self.context['workflow_instance']
        attrs['transition'] = WorkflowTransition.objects.get(
            pk=attrs.pop('transition_pk')
        )

        instance = WorkflowInstanceLogEntry(**attrs)

        try:
            instance.full_clean()
        except DjangoValidationError as exception:
            raise ValidationError(exception)

        return attrs
"""

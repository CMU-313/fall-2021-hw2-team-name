from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.views import (
    FormView, MultipleObjectConfirmActionView, SingleObjectEditView,
    SingleObjectListView
)
from mayan.apps.documents.forms import DocumentTypeFilteredSelectForm
from mayan.apps.documents.models import Document, DocumentType

from .icons import icon_file_metadata
from .models import DocumentVersionDriverEntry
from .permissions import (
    permission_document_type_file_metadata_setup,
    permission_file_metadata_submit, permission_file_metadata_view
)


class DocumentDriverListView(SingleObjectListView):
    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_file_metadata,
            'no_results_text': _(
                'File metadata are the attributes of the document\'s file. '
                'They can range from camera information used to take a photo '
                'to the author that created a file. File metadata are set '
                'when the document\'s file was first created. File metadata '
                'attributes reside in the file itself. They are not the '
                'same as the document metadata, which are user defined and '
                'reside in the database.'
            ),
            'no_results_title': _('No file metadata available.'),
            'object': self.get_object(),
            'title': _(
                'File metadata drivers for: %s'
            ) % self.get_object(),
        }

    def get_object(self):
        document = get_object_or_404(klass=Document, pk=self.kwargs['pk'])
        AccessControlList.objects.check_access(
            permissions=permission_file_metadata_view,
            user=self.request.user, obj=document
        )
        return document

    def get_object_list(self):
        return self.get_object().latest_version.file_metadata_drivers.all()


class DocumentVersionDriverEntryFileMetadataListView(SingleObjectListView):
    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_title': _('No file metadata available.'),
            'object': self.get_object().document_version.document,
            'title': _(
                'File metadata attribures for: %(document)s, for driver: %(driver)s'
            ) % {
                'document': self.get_object().document_version.document,
                'driver': self.get_object().driver
            },
        }

    def get_object(self):
        document_version_driver_entry = get_object_or_404(
            klass=DocumentVersionDriverEntry, pk=self.kwargs['pk']
        )
        AccessControlList.objects.check_access(
            obj=document_version_driver_entry.document_version,
            permissions=permission_file_metadata_view,
            user=self.request.user,
        )
        return document_version_driver_entry

    def get_object_list(self):
        return self.get_object().entries.all()


class DocumentSubmitView(MultipleObjectConfirmActionView):
    model = Document
    object_permission = permission_file_metadata_submit
    success_message = '%(count)d document submitted to the file metadata queue.'
    success_message_plural = '%(count)d documents submitted to the file metadata queue.'

    def get_extra_context(self):
        queryset = self.get_queryset()

        result = {
            'title': ungettext(
                'Submit the selected document to the file metadata queue?',
                'Submit the selected documents to the file metadata queue?',
                queryset.count()
            )
        }

        return result

    def object_action(self, form, instance):
        instance.submit_for_file_metadata_processing()


class DocumentTypeSettingsEditView(SingleObjectEditView):
    fields = ('auto_process',)
    object_permission = permission_document_type_file_metadata_setup
    post_action_redirect = reverse_lazy('documents:document_type_list')

    def get_document_type(self):
        return get_object_or_404(klass=DocumentType, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'object': self.get_document_type(),
            'title': _(
                'Edit file metadata settings for document type: %s'
            ) % self.get_document_type()
        }

    def get_object(self, queryset=None):
        return self.get_document_type().file_metadata_settings


class DocumentTypeSubmitView(FormView):
    extra_context = {
        'title': _(
            'Submit all documents of a type for file metadata processing.'
        )
    }
    form_class = DocumentTypeFilteredSelectForm
    post_action_redirect = reverse_lazy('common:tools_list')

    def get_form_extra_kwargs(self):
        return {
            'allow_multiple': True,
            'permission': permission_file_metadata_submit,
            'user': self.request.user
        }

    def form_valid(self, form):
        count = 0
        for document_type in form.cleaned_data['document_type']:
            for document in document_type.documents.all():
                document.submit_for_file_metadata_processing()
                count += 1

        messages.success(
            self.request, _(
                '%(count)d documents added to the file metadata processing '
                'queue.'
            ) % {
                'count': count,
            }
        )

        return HttpResponseRedirect(self.get_success_url())

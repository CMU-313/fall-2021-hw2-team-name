from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.generics import (
    FormView, MultipleObjectConfirmActionView, SingleObjectDetailView,
    SingleObjectDownloadView, SingleObjectEditView, SingleObjectListView
)
from mayan.apps.common.mixins import ExternalObjectMixin
from mayan.apps.documents.forms import DocumentTypeFilteredSelectForm
from mayan.apps.documents.mixins import RecentDocumentMixin
from mayan.apps.documents.models import Document, DocumentPage, DocumentType

from .forms import DocumentPageOCRContentForm, DocumentOCRContentForm
from .models import DocumentVersionOCRError
from .permissions import (
    permission_ocr_content_view, permission_ocr_document,
    permission_document_type_ocr_setup
)
from .utils import get_document_content_iterator


class DocumentOCRContentView(RecentDocumentMixin, SingleObjectDetailView):
    form_class = DocumentOCRContentForm
    model = Document
    object_permission = permission_ocr_content_view
    pk_url_kwarg = 'document_id'

    def get_extra_context(self):
        return {
            'document': self.get_object(),
            'hide_labels': True,
            'object': self.get_object(),
            'title': _('OCR result for document: %s.') % self.get_object(),
        }


class DocumentOCRDownloadView(RecentDocumentMixin, SingleObjectDownloadView):
    model = Document
    object_permission = permission_ocr_content_view
    pk_url_kwarg = 'document_id'

    def get_file(self):
        file_object = DocumentOCRDownloadView.TextIteratorIO(
            iterator=get_document_content_iterator(document=self.object)
        )
        return DocumentOCRDownloadView.VirtualFile(
            file=file_object, name='{}-OCR'.format(self.object)
        )


class DocumentOCRErrorsListView(SingleObjectListView):
    object_permission = permission_ocr_document

    def get_document(self):
        return get_object_or_404(
            klass=Document, pk=self.kwargs['document_id']
        )

    def get_extra_context(self):
        return {
            'hide_object': True,
            'object': self.get_document(),
            'title': _('OCR errors for document: %s.') % self.get_document(),
        }

    def get_object_list(self):
        return self.get_document().latest_version.ocr_errors.all()


class DocumentPageOCRContentView(RecentDocumentMixin, SingleObjectDetailView):
    form_class = DocumentPageOCRContentForm
    model = DocumentPage
    object_permission = permission_ocr_content_view
    pk_url_kwarg = 'document_page_id'

    def get_extra_context(self):
        return {
            'hide_labels': True,
            'object': self.object,
            'title': _('OCR result for document page: %s.') % self.object,
        }

    def get_recent_document(self):
        return self.object.document


class DocumentSubmitView(MultipleObjectConfirmActionView):
    model = Document
    object_permission = permission_ocr_document
    pk_url_kwarg = 'document_id'
    success_message_single = _('Document "%(object)s" added to the OCR queue.')
    success_message_singular = _('%(count)d document submitted to the OCR queue.')
    success_message_plural = _('%(count)d documents submitted to the OCR queue.')
    title_single = _('Submit the document "%(object)s" to the OCR queue.')
    title_singular = _('Submit the selected document to the OCR queue.')
    title_plural = _('Submit the selected documents to the OCR queue.')

    def object_action(self, form, instance):
        instance.submit_for_ocr()


class DocumentTypeSettingsEditView(ExternalObjectMixin, SingleObjectEditView):
    external_object_class = DocumentType
    external_object_permission = permission_document_type_ocr_setup
    external_object_pk_url_kwarg = 'document_type_id'
    fields = ('auto_ocr',)
    post_action_redirect = reverse_lazy(
        viewname='documents:document_type_list'
    )

    def get_document_type(self):
        return self.external_object

    def get_extra_context(self):
        return {
            'object': self.get_document_type(),
            'title': _(
                'Edit OCR settings for document type: %s.'
            ) % self.get_document_type()
        }

    def get_object(self, queryset=None):
        return self.get_document_type().ocr_settings


class DocumentTypeSubmitView(FormView):
    extra_context = {
        'title': _('Submit all documents of a type for OCR.')
    }
    form_class = DocumentTypeFilteredSelectForm
    post_action_redirect = reverse_lazy(viewname='common:tools_list')

    def get_form_extra_kwargs(self):
        return {
            'allow_multiple': True,
            'permission': permission_ocr_document,
            'user': self.request.user
        }

    def form_valid(self, form):
        count = 0
        for document_type in form.cleaned_data['document_type']:
            for document in document_type.documents.all():
                document.submit_for_ocr()
                count += 1

        messages.success(
            message=_(
                '%(count)d documents added to the OCR queue.'
            ) % {
                'count': count,
            }, request=self.request
        )

        return HttpResponseRedirect(redirect_to=self.get_success_url())


class EntryListView(SingleObjectListView):
    extra_context = {
        'hide_object': True,
        'title': _('OCR errors.'),
    }
    view_permission = permission_document_type_ocr_setup

    def get_object_list(self):
        return DocumentVersionOCRError.objects.all()

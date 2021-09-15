from __future__ import absolute_import, unicode_literals

import logging

from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.generics import (
    ConfirmView, MultipleObjectConfirmActionView
)

from ..icons import icon_trashed_document_list
from ..models import Document, TrashedDocument
from ..permissions import (
    permission_document_trash, permission_document_view, permission_empty_trash,
    permission_trashed_document_delete, permission_trashed_document_restore
)
from ..tasks import task_delete_document

from .document_views import DocumentListView

__all__ = (
    'DocumentTrashView', 'EmptyTrashCanView', 'TrashedDocumentDeleteView',
    'TrashedDocumentListView', 'TrashedDocumentRestoreView',
)
logger = logging.getLogger(__name__)


class DocumentTrashView(MultipleObjectConfirmActionView):
    model = Document
    object_permission = permission_document_trash
    pk_url_kwarg = 'document_id'
    success_message_singular = _(
        '%(count)d document moved to the trash.'
    )
    success_message_plural = _(
        '%(count)d documents moved to the trash.'
    )

    def get_extra_context(self):
        queryset = self.get_object_list()

        result = {
            'title': ungettext(
                single='Move the selected document to the trash?',
                plural='Move the selected documents to the trash?',
                number=queryset.count()
            )
        }

        return result

    def object_action(self, form, instance):
        instance.delete()


class EmptyTrashCanView(ConfirmView):
    extra_context = {
        'title': _('Empty trash?')
    }
    view_permission = permission_empty_trash
    action_cancel_redirect = post_action_redirect = reverse_lazy(
        viewname='documents:trashed_document_list'
    )

    def view_action(self):
        for trashed_document in TrashedDocument.objects.all():
            task_delete_document.apply_async(
                kwargs={'trashed_document_id': trashed_document.pk}
            )

        messages.success(
            request=self.request, message=_('Trash emptied successfully')
        )


class TrashedDocumentDeleteView(MultipleObjectConfirmActionView):
    model = TrashedDocument
    object_permission = permission_trashed_document_delete
    pk_url_kwarg = 'trashed_document_id'
    success_message_singular = _(
        '%(count)d trashed document deleted.'
    )
    success_message_plural = _(
        '%(count)d trashed documents deleted.'
    )

    def get_extra_context(self):
        queryset = self.get_object_list()

        result = {
            'title': ungettext(
                single='Delete the selected trashed document?',
                plural='Delete the selected trashed documents?',
                number=queryset.count()
            )
        }

        return result

    def object_action(self, form, instance):
        instance.delete()


class TrashedDocumentListView(DocumentListView):
    object_permission = None

    def get_document_queryset(self):
        return AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=TrashedDocument.trash.all(), user=self.request.user
        )

    def get_extra_context(self):
        context = super(TrashedDocumentListView, self).get_extra_context()
        context.update(
            {
                'hide_link': True,
                'no_results_icon': icon_trashed_document_list,
                'no_results_text': _(
                    'To avoid loss of data, documents are not deleted '
                    'instantly. First, they are placed in the trash can. '
                    'From here they can be then finally deleted or restored.'
                ),
                'no_results_title': _(
                    'There are no documents in the trash can'
                ),
                'title': _('Documents in trash'),
            }
        )
        return context


class TrashedDocumentRestoreView(MultipleObjectConfirmActionView):
    model = TrashedDocument
    object_permission = permission_trashed_document_restore
    pk_url_kwarg = 'trashed_document_id'
    success_message_singular = _(
        '%(count)d trashed document restored.'
    )
    success_message_plural = _(
        '%(count)d trashed documents restored.'
    )

    def get_extra_context(self):
        queryset = self.get_object_list()

        result = {
            'title': ungettext(
                single='Restore the selected trashed document?',
                plural='Restore the selected trashed documents?',
                number=queryset.count()
            )
        }

        return result

    def object_action(self, form, instance):
        instance.restore()

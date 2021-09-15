from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _, ungettext

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.generics import (
    MultipleObjectConfirmActionView, MultipleObjectFormActionView,
    SingleObjectDetailView
)
from mayan.apps.common.utils import encapsulate
from mayan.apps.documents.models import Document
from mayan.apps.documents.views import DocumentListView

from .forms import DocumentCheckoutDefailForm, DocumentCheckoutForm
from .icons import icon_checkout_info
from .models import DocumentCheckout
from .permissions import (
    permission_document_check_in, permission_document_checkout,
    permission_document_checkout_detail_view
)


class DocumentCheckinView(MultipleObjectConfirmActionView):
    error_message = 'Unable to check in document "%(instance)s". %(exception)s'
    model = Document
    object_permission = permission_document_check_in
    pk_url_kwarg = 'document_id'
    success_message_singular = '%(count)d document checked in.'
    success_message_plural = '%(count)d documents checked in.'

    def get_extra_context(self):
        queryset = self.get_object_list()

        result = {
            'title': ungettext(
                singular='Check in %(count)d document',
                plural='Check in %(count)d documents',
                number=queryset.count()
            ) % {
                'count': queryset.count(),
            }
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _(
                        'Check in document: %s'
                    ) % queryset.first()
                }
            )

        return result

    def get_post_object_action_url(self):
        if self.action_count == 1:
            return reverse(
                viewname='checkouts:document_checkout_info',
                kwargs={'document_id': self.action_id_list[0]}
            )
        else:
            super(DocumentCheckinView, self).get_post_action_redirect()

    def object_action(self, form, instance):
        DocumentCheckout.objects.check_in_document(
            document=instance, user=self.request.user
        )


class DocumentCheckoutView(MultipleObjectFormActionView):
    error_message = 'Unable to checkout document "%(instance)s". %(exception)s'
    form_class = DocumentCheckoutForm
    model = Document
    object_permission = permission_document_checkout
    pk_url_kwarg = 'document_id'
    success_message_singular = '%(count)d document checked out.'
    success_message_plural = '%(count)d documents checked out.'

    def get_extra_context(self):
        queryset = self.get_object_list()

        result = {
            'title': ungettext(
                singular='Checkout %(count)d document',
                plural='Checkout %(count)d documents',
                number=queryset.count()
            ) % {
                'count': queryset.count(),
            }
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _(
                        'Check out document: %s'
                    ) % queryset.first()
                }
            )

        return result

    def get_post_object_action_url(self):
        if self.action_count == 1:
            return reverse(
                viewname='checkouts:document_checkout_info',
                kwargs={'document_id': self.action_id_list[0]}
            )
        else:
            super(DocumentCheckoutView, self).get_post_action_redirect()

    def object_action(self, form, instance):
        DocumentCheckout.objects.checkout_document(
            block_new_version=form.cleaned_data['block_new_version'],
            document=instance,
            expiration_datetime=form.cleaned_data['expiration_datetime'],
            user=self.request.user,
        )


class DocumentCheckoutDetailView(SingleObjectDetailView):
    form_class = DocumentCheckoutDefailForm
    model = Document
    object_permission = permission_document_checkout_detail_view

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _(
                'Check out details for document: %s'
            ) % self.get_object()
        }

    def get_object(self):
        return get_object_or_404(klass=Document, pk=self.kwargs['document_id'])


class DocumentCheckoutListView(DocumentListView):
    def get_document_queryset(self):
        return AccessControlList.objects.restrict_queryset(
            permission=permission_document_checkout_detail_view,
            queryset=DocumentCheckout.objects.checked_out_documents(),
            user=self.request.user
        )

    def get_extra_context(self):
        context = super(DocumentCheckoutListView, self).get_extra_context()
        context.update(
            {
                'extra_columns': (
                    {
                        'name': _('User'),
                        'attribute': encapsulate(
                            lambda document: document.get_checkout_info().user.get_full_name() or document.get_checkout_info().user
                        )
                    },
                    {
                        'name': _('Checkout time and date'),
                        'attribute': encapsulate(
                            lambda document: document.get_checkout_info().checkout_datetime
                        )
                    },
                    {
                        'name': _('Checkout expiration'),
                        'attribute': encapsulate(
                            lambda document: document.get_checkout_info().expiration_datetime
                        )
                    },
                ),
                'no_results_icon': icon_checkout_info,
                'no_results_text': _(
                    'Checking out a document blocks certain document '
                    'operations for a predetermined amount of '
                    'time.'
                ),
                'no_results_title': _('No documents have been checked out'),
                'title': _('Documents checked out'),
            }
        )
        return context

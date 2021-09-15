from __future__ import absolute_import, unicode_literals

import logging

from django.contrib import messages
from django.core.files import File
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.generics import (
    ConfirmView, FormView, SingleObjectCreateView, SingleObjectDeleteView,
    SingleObjectDetailView, SingleObjectDownloadView, SingleObjectListView
)
from mayan.apps.common.mixins import ExternalObjectMixin
from mayan.apps.django_gpg.exceptions import NeedPassphrase, PassphraseError
from mayan.apps.documents.models import DocumentVersion
from mayan.apps.storage.utils import TemporaryFile

from .forms import (
    DocumentVersionSignatureCreateForm, DocumentVersionSignatureDetailForm
)
from .icons import icon_document_signature_list
from .links import (
    link_document_version_signature_detached_create,
    link_document_version_signature_embedded_create,
    link_document_version_signature_upload
)
from .models import DetachedSignature, SignatureBaseModel
from .permissions import (
    permission_document_version_sign_detached,
    permission_document_version_sign_embedded,
    permission_document_version_signature_delete,
    permission_document_version_signature_download,
    permission_document_version_signature_upload,
    permission_document_version_signature_verify,
    permission_document_version_signature_view
)
from .tasks import task_verify_missing_embedded_signature

logger = logging.getLogger(__name__)


class DocumentVersionDetachedSignatureCreateView(ExternalObjectMixin, FormView):
    external_object_class = DocumentVersion
    external_object_permission = permission_document_version_sign_detached
    external_object_pk_url_kwarg = 'document_version_id'
    form_class = DocumentVersionSignatureCreateForm

    def form_valid(self, form):
        key = form.cleaned_data['key']
        passphrase = form.cleaned_data['passphrase'] or None

        try:
            with self.get_document_version().open() as file_object:
                detached_signature = key.sign_file(
                    file_object=file_object, detached=True,
                    passphrase=passphrase
                )
        except NeedPassphrase:
            messages.error(
                message=_('Passphrase is needed to unlock this key.'),
                request=self.request
            )
            return HttpResponseRedirect(
                redirect_to=reverse(
                    viewname='signatures:document_version_signature_detached_create',
                    kwargs={'document_version_id': self.get_document_version().pk}
                )
            )
        except PassphraseError:
            messages.error(
                message=_('Passphrase is incorrect.'), request=self.request
            )
            return HttpResponseRedirect(
                redirect_to=reverse(
                    viewname='signatures:document_version_signature_detached_create',
                    kwargs={'document_version_id': self.get_document_version().pk}
                )
            )
        else:
            temporary_file_object = TemporaryFile()
            temporary_file_object.write(detached_signature.data)
            temporary_file_object.seek(0)

            DetachedSignature.objects.create(
                document_version=self.get_document_version(),
                signature_file=File(temporary_file_object)
            )

            temporary_file_object.close()

            messages.success(
                message=_('Document version signed successfully.'),
                request=self.request
            )

        return super(
            DocumentVersionDetachedSignatureCreateView, self
        ).form_valid(form)

    def get_document_version(self):
        return self.get_external_object()

    def get_extra_context(self):
        return {
            'object': self.get_document_version(),
            'title': _(
                'Sign document version "%s" with a detached signature'
            ) % self.get_document_version(),
        }

    def get_form_extra_kwargs(self):
        return {'user': self.request.user}

    def get_post_action_redirect(self):
        return reverse(
            viewname='signatures:document_version_signature_list',
            kwargs={'document_version_id': self.get_document_version().pk}
        )


class DocumentVersionEmbeddedSignatureCreateView(FormView):
    external_object_class = DocumentVersion
    external_object_permission = permission_document_version_sign_embedded
    external_object_pk_url_kwarg = 'document_version_id'
    form_class = DocumentVersionSignatureCreateForm

    def form_valid(self, form):
        key = form.cleaned_data['key']
        passphrase = form.cleaned_data['passphrase'] or None

        try:
            with self.get_document_version().open() as file_object:
                signature_result = key.sign_file(
                    binary=True, file_object=file_object, passphrase=passphrase
                )
        except NeedPassphrase:
            messages.error(
                message=_('Passphrase is needed to unlock this key.'),
                request=self.request
            )
            return HttpResponseRedirect(
                redirect_to=reverse(
                    viewname='signatures:document_version_signature_embedded_create',
                    kwargs={'document_version_id': self.get_document_version().pk}
                )
            )
        except PassphraseError:
            messages.error(
                message=_('Passphrase is incorrect.'), request=self.request
            )
            return HttpResponseRedirect(
                redirect_to=reverse(
                    viewname='signatures:document_version_signature_embedded_create',
                    kwargs={'document_version_id': self.get_document_version().pk}
                )
            )
        else:
            temporary_file_object = TemporaryFile()
            temporary_file_object.write(signature_result.data)
            temporary_file_object.seek(0)

            new_version = self.get_document_version().document.new_version(
                file_object=temporary_file_object, _user=self.request.user
            )

            temporary_file_object.close()

            messages.success(
                message=_('Document version signed successfully.'),
                request=self.request
            )

            return HttpResponseRedirect(
                redirect_to=reverse(
                    viewname='signatures:document_version_signature_list',
                    kwargs={'document_version_id': new_version.pk}
                )
            )

        return super(
            DocumentVersionEmbeddedSignatureCreateView, self
        ).form_valid(form)

    def get_document_version(self):
        return self.get_external_object()

    def get_extra_context(self):
        return {
            'object': self.get_document_version(),
            'title': _(
                'Sign document version "%s" with a embedded signature'
            ) % self.get_document_version(),
        }

    def get_form_extra_kwargs(self):
        return {'user': self.request.user}


class DocumentVersionSignatureDeleteView(SingleObjectDeleteView):
    object_permission = permission_document_version_signature_delete
    pk_url_kwarg = 'signature_id'

    def get_extra_context(self):
        return {
            'object': self.get_object().document_version,
            'signature': self.get_object(),
            'title': _('Delete detached signature: %s') % self.get_object()
        }

    def get_post_action_redirect(self):
        return reverse(
            viewname='signatures:document_version_signature_list',
            kwargs={'document_version_id': self.get_object().document_version.pk}
        )

    def get_source_queryset(self):
        return SignatureBaseModel.objects.select_subclasses()


class DocumentVersionSignatureDetailView(SingleObjectDetailView):
    form_class = DocumentVersionSignatureDetailForm
    object_permission = permission_document_version_signature_view
    pk_url_kwarg = 'signature_id'

    def get_extra_context(self):
        return {
            'hide_object': True,
            'object': self.get_object().document_version,
            'signature': self.get_object(),
            'title': _(
                'Details for signature: %s'
            ) % self.get_object(),
        }

    def get_source_queryset(self):
        return SignatureBaseModel.objects.select_subclasses()


class DocumentVersionSignatureDownloadView(SingleObjectDownloadView):
    object_permission = permission_document_version_signature_download
    pk_url_kwarg = 'signature_id'

    def get_file(self):
        signature = self.get_object()

        return DocumentVersionSignatureDownloadView.VirtualFile(
            signature.signature_file, name=force_text(signature)
        )

    def get_source_queryset(self):
        return SignatureBaseModel.objects.select_subclasses()


class DocumentVersionSignatureListView(ExternalObjectMixin, SingleObjectListView):
    external_object_class = DocumentVersion
    external_object_permission = permission_document_version_signature_view
    external_object_pk_url_kwarg = 'document_version_id'

    def get_document_version(self):
        return self.get_external_object()

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_document_signature_list,
            'no_results_text': _(
                'Signatures help provide authorship evidence and tamper '
                'detection. They are very secure and hard to '
                'forge. A signature can be embedded as part of the document '
                'itself or uploaded as a separate file.'
            ),
            'no_results_secondary_links': [
                link_document_version_signature_detached_create.resolve(
                    RequestContext(
                        self.request, {'object': self.get_document_version()}
                    )
                ),
                link_document_version_signature_embedded_create.resolve(
                    RequestContext(
                        self.request, {'object': self.get_document_version()}
                    )
                ),
                link_document_version_signature_upload.resolve(
                    RequestContext(
                        self.request, {'object': self.get_document_version()}
                    )
                ),
            ],
            'no_results_title': _('There are no signatures for this document.'),
            'object': self.get_document_version(),
            'title': _(
                'Signatures for document version: %s'
            ) % self.get_document_version(),
        }

    def get_source_queryset(self):
        return self.get_document_version().signatures.all()


class DocumentVersionSignatureUploadView(ExternalObjectMixin, SingleObjectCreateView):
    external_object_class = DocumentVersion
    external_object_permission = permission_document_version_signature_upload
    external_object_pk_url_kwarg = 'document_version_id'
    fields = ('signature_file',)
    model = DetachedSignature

    def get_document_version(self):
        return self.get_external_object()

    def get_extra_context(self):
        return {
            'object': self.get_document_version(),
            'title': _(
                'Upload detached signature for document version: %s'
            ) % self.get_document_version(),
        }

    def get_instance_extra_data(self):
        return {'document_version': self.get_document_version()}

    def get_post_action_redirect(self):
        return reverse(
            viewname='signatures:document_version_signature_list',
            kwargs={'document_version_id': self.get_document_version().pk}
        )


class AllDocumentSignatureVerifyView(ConfirmView):
    extra_context = {
        'message': _(
            'On large databases this operation may take some time to execute.'
        ), 'title': _('Verify all document for signatures?'),
    }
    view_permission = permission_document_version_signature_verify

    def get_post_action_redirect(self):
        return reverse(viewname='common:tools_list')

    def view_action(self):
        task_verify_missing_embedded_signature.delay()
        messages.success(
            message=_('Signature verification queued successfully.'),
            request=self.request
        )

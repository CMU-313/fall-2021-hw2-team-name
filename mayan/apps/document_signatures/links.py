from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation import Link

from .icons import (
    icon_all_document_version_signature_verify, icon_document_signature_list,
    link_document_version_signature_detached_create,
    icon_document_version_signature_embedded_create,
    icon_document_version_signature_list, icon_document_version_signature_upload
)
from .literals import SIGNATURE_TYPE_DETACHED
from .permissions import (
    permission_document_version_sign_detached,
    permission_document_version_sign_embedded,
    permission_document_version_signature_delete,
    permission_document_version_signature_download,
    permission_document_version_signature_upload,
    permission_document_version_signature_verify,
    permission_document_version_signature_view
)


def is_detached_signature(context):
    return context['object'].signature_type == SIGNATURE_TYPE_DETACHED


link_all_document_version_signature_verify = Link(
    icon_class=icon_all_document_version_signature_verify,
    permission=permission_document_version_signature_verify,
    text=_('Verify all documents'),
    view='signatures:all_document_version_signature_verify'
)
link_document_signature_list = Link(
    icon_class=icon_document_signature_list,
    kwargs={'document_version_id': 'resolved_object.latest_version.pk'},
    permission=permission_document_version_signature_view,
    text=_('Signatures'), view='signatures:document_version_signature_list'
)
link_document_version_signature_delete = Link(
    condition=is_detached_signature,
    kwargs={'signature_id': 'resolved_object.pk'},
    permission=permission_document_version_signature_delete,
    tags='dangerous', text=_('Delete'),
    view='signatures:document_version_signature_delete'
)
link_document_version_signature_details = Link(
    kwargs={'signature_id': 'resolved_object.pk'},
    permission=permission_document_version_signature_view,
    text=_('Details'), view='signatures:document_version_signature_details'
)
link_document_version_signature_list = Link(
    icon_class=icon_document_version_signature_list,
    kwargs={'document_version_id': 'resolved_object.pk'},
    permission=permission_document_version_signature_view,
    text=_('Signatures'), view='signatures:document_version_signature_list'
)
link_document_version_signature_download = Link(
    condition=is_detached_signature,
    kwargs={'signature_id': 'resolved_object.pk'},
    permission=permission_document_version_signature_download,
    text=_('Download'), view='signatures:document_version_signature_download'
)
link_document_version_signature_upload = Link(
    icon_class=icon_document_version_signature_upload,
    kwargs={'document_version_id': 'resolved_object.pk'},
    permission=permission_document_version_signature_upload,
    text=_('Upload signature'),
    view='signatures:document_version_signature_upload'
)
link_document_version_signature_detached_create = Link(
    icon_class=link_document_version_signature_detached_create,
    kwargs={'document_version_id': 'resolved_object.pk'},
    permission=permission_document_version_sign_detached,
    text=_('Sign detached'),
    view='signatures:document_version_signature_detached_create'
)
link_document_version_signature_embedded_create = Link(
    icon_class=icon_document_version_signature_embedded_create,
    kwargs={'document_version_id': 'resolved_object.pk'},
    permission=permission_document_version_sign_embedded,
    text=_('Sign embedded'),
    view='signatures:document_version_signature_embedded_create'
)

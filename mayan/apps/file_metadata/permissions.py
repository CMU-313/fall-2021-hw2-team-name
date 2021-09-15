from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(label=_('File metadata'), name='file_metadata')

permission_document_type_file_metadata_setup = namespace.add_permission(
    name='file_metadata_document_type_setup',
    label=_('Change document type file metadata settings')
)
permission_file_metadata_submit = namespace.add_permission(
    name='file_metadata_submit', label=_(
        'Submit document for file metadata processing'
    )
)
permission_file_metadata_view = namespace.add_permission(
    name='file_metadata_view', label=_('View file metadata')
)

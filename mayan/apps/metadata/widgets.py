from __future__ import unicode_literals

from django.utils.html import format_html_join
from django.utils.translation import ugettext_lazy as _


def widget_get_metadata_string(context, attribute=None):
    """
    Return a formated representation of a document's metadata values
    """
    obj = context['object']

    if attribute:
        obj = getattr(context['object'], attribute)

    return format_html_join(
        '\n', '<div class="metadata-display"><b>{}: </b><span data-metadata-type="{}" data-pk="{}">{}</span></div>',
        (
            (
                document_metadata.metadata_type, document_metadata.metadata_type_id, document_metadata.id, document_metadata.value
            ) for document_metadata in obj.metadata.all()
        )
    )


widget_get_metadata_string.short_description = _('Metadata')

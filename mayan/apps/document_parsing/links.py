from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation import Link, get_cascade_condition

from .icons import (
    icon_document_content, icon_document_content_download,
    icon_document_multiple_submit, icon_document_parsing_errors_list,
    icon_document_submit, icon_document_type_parsing_settings,
    icon_document_type_submit, icon_link_error_list
)
from .permissions import (
    permission_content_view, permission_document_type_parsing_setup,
    permission_parse_document
)

link_document_content = Link(
    icon_class=icon_document_content,
    kwargs={'document_id': 'resolved_object.id'},
    permission=permission_content_view, text=_('Content'),
    view='document_parsing:document_content',
)
link_document_page_content = Link(
    icon_class=icon_document_content,
    kwargs={'document_page_id': 'resolved_object.id'},
    permission=permission_content_view, text=_('Content'),
    view='document_parsing:document_page_content',
)
link_document_parsing_errors_list = Link(
    icon_class=icon_document_parsing_errors_list,
    kwargs={'document_id': 'resolved_object.id'},
    permission=permission_content_view, text=_('Parsing errors'),
    view='document_parsing:document_parsing_error_list'
)
link_document_content_download = Link(
    icon_class=icon_document_content_download,
    kwargs={'document_id': 'resolved_object.id'},
    permission=permission_content_view, text=_('Download content'),
    view='document_parsing:document_content_download'
)
link_document_multiple_submit = Link(
    icon_class=icon_document_multiple_submit, text=_('Submit for parsing'),
    view='document_parsing:document_multiple_submit'
)
link_document_submit = Link(
    icon_class=icon_document_submit,
    kwargs={'document_id': 'resolved_object.id'},
    permission=permission_parse_document,
    text=_('Submit for parsing'), view='document_parsing:document_submit'
)
link_document_type_parsing_settings = Link(
    icon_class=icon_document_type_parsing_settings,
    kwargs={'document_type_id': 'resolved_object.id'},
    permission=permission_document_type_parsing_setup,
    text=_('Setup parsing'),
    view='document_parsing:document_type_parsing_settings',
)
link_document_type_submit = Link(
    condition=get_cascade_condition(
        app_label='documents', model_name='DocumentType',
        object_permission=permission_document_type_parsing_setup
    ), icon_class=icon_document_type_submit,
    text=_('Parse documents per type'),
    view='document_parsing:document_type_submit'
)
link_error_list = Link(
    icon_class=icon_link_error_list, permission=permission_content_view,
    text=_('Parsing errors'), view='document_parsing:error_list'
)

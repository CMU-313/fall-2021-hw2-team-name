from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation import Link

from .icons import (
    icon_document_content, icon_document_multiple_submit,
    icon_document_ocr_download, icon_document_ocr_errors_list,
    icon_document_type_ocr_settings, icon_document_submit,
    icon_document_type_submit, icon_entry_list
)
from .permissions import (
    permission_ocr_content_view, permission_ocr_document,
    permission_document_type_ocr_setup
)

link_document_page_ocr_content = Link(
    icon_class=icon_document_content,
    kwargs={'document_page_id': 'resolved_object.id'},
    permission=permission_ocr_content_view, text=_('OCR'),
    view='ocr:document_page_content'
)
link_document_ocr_content = Link(
    icon_class=icon_document_content,
    kwargs={'document_id': 'resolved_object.id'},
    permission=permission_ocr_content_view, text=_('OCR'),
    view='ocr:document_content'
)
link_document_submit = Link(
    icon_class=icon_document_submit,
    kwargs={'document_id': 'resolved_object.id'},
    permission=permission_ocr_document, text=_('Submit for OCR'),
    view='ocr:document_submit'
)
link_document_multiple_submit = Link(
    icon_class=icon_document_multiple_submit, text=_('Submit for OCR'),
    view='ocr:document_multiple_submit'
)
link_document_type_ocr_settings = Link(
    icon_class=icon_document_type_ocr_settings,
    kwargs={'document_type_id': 'resolved_object.id'},
    permission=permission_document_type_ocr_setup, text=_('Setup OCR'),
    view='ocr:document_type_settings'
)
link_document_type_submit = Link(
    icon_class=icon_document_type_submit,
    permission=permission_ocr_document, text=_('OCR documents per type'),
    view='ocr:document_type_submit'
)
link_entry_list = Link(
    icon_class=icon_entry_list, permission=permission_ocr_document,
    text=_('OCR errors'), view='ocr:entry_list'
)
link_document_ocr_errors_list = Link(
    icon_class=icon_document_ocr_errors_list,
    kwargs={'document_id': 'resolved_object.id'},
    permission=permission_ocr_content_view, text=_('OCR errors'),
    view='ocr:document_error_list'
)
link_document_ocr_download = Link(
    icon_class=icon_document_ocr_download,
    kwargs={'document_id': 'resolved_object.id'},
    permission=permission_ocr_content_view, text=_('Download OCR text'),
    view='ocr:document_download'
)

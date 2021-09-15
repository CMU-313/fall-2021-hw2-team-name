from __future__ import unicode_literals

from datetime import timedelta

from django.apps import apps
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.settings import settings_db_sync_task_delay

from .events import event_ocr_document_version_submit
from .tasks import task_do_ocr


def method_document_get_ocr_content(self):
    latest_version = self.latest_version
    # Don't error out if document has no version
    if latest_version:
        return latest_version.get_ocr_content()


method_document_get_ocr_content.short_description = _(
    'get_ocr_content()'
)
method_document_get_ocr_content.help_text = _(
    'Return the OCR content of the document.'
)


def method_document_ocr_submit(self, _user=None):
    latest_version = self.latest_version
    # Don't error out if document has no version
    if latest_version:
        latest_version.submit_for_ocr(_user=_user)


def method_document_page_get_ocr_content(self):
    DocumentPageOCRContent = apps.get_model(
        app_label='ocr', model_name='DocumentPageOCRContent'
    )

    try:
        page_content = self.ocr_content.content
    except DocumentPageOCRContent.DoesNotExist:
        return ''
    else:
        return page_content


def method_document_version_get_ocr_content(self):
    result = []
    for page in self.pages.all():
        result.append(page.get_ocr_content())

    return ''.join(result)


def method_document_version_ocr_submit(self, _user=None):
    event_ocr_document_version_submit.commit(
        action_object=self.document, actor=_user, target=self
    )

    task_do_ocr.apply_async(
        eta=now() + timedelta(seconds=settings_db_sync_task_delay.value),
        kwargs={'document_version_pk': self.pk},
    )

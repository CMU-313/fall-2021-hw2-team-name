from __future__ import unicode_literals

from datetime import timedelta

from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.settings import settings_db_sync_task_delay

from .events import event_ocr_document_version_submit
from .tasks import task_do_ocr
from .utils import get_document_version_content_iterator


def method_document_ocr_submit(self):
    latest_version = self.latest_version
    # Don't error out if document has no version
    if latest_version:
        latest_version.submit_for_ocr()


def method_document_version_ocr_submit(self):
    event_ocr_document_version_submit.commit(
        action_object=self.document, target=self
    )

    task_do_ocr.apply_async(
        eta=now() + timedelta(seconds=settings_db_sync_task_delay.value),
        kwargs={'document_version_pk': self.pk},
    )


def method_get_document_ocr_content(self):
    latest_version = self.latest_version
    # Don't error out if document has no version
    if latest_version:
        return latest_version.get_ocr_content()


method_get_document_ocr_content.short_description = _(
    'get_ocr_content()'
)
method_get_document_ocr_content.help_text = _(
    'Return the OCR content of the document.'
)


def method_get_document_version_ocr_content(self):
    return ' '.join(
        get_document_version_content_iterator(document_version=self)
    )

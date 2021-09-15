from __future__ import unicode_literals

from datetime import timedelta

from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.settings import settings_db_sync_task_delay

from .events import event_parsing_document_version_submit
from .tasks import task_parse_document_version
from .utils import get_document_version_content_iterator


def method_document_submit_for_parsing(self):
    latest_version = self.latest_version
    # Don't error out if document has no version
    if latest_version:
        latest_version.submit_for_parsing()


def method_document_version_submit_for_parsing(self):
    event_parsing_document_version_submit.commit(
        action_object=self.document, target=self
    )

    task_parse_document_version.apply_async(
        eta=now() + timedelta(seconds=settings_db_sync_task_delay.value),
        kwargs={'document_version_pk': self.pk},
    )


def method_get_document_content(self):
    latest_version = self.latest_version

    if latest_version:
        return latest_version.get_content()


method_get_document_content.help_text = _(
    'Return the parsed content of the document.'
)
method_get_document_content.short_description = _(
    'get_content()'
)


def method_get_document_version_content(self):
    return ' '.join(
        get_document_version_content_iterator(document_version=self)
    )


method_get_document_version_content.help_text = _(
    'Return the parsed content of the document version.'
)

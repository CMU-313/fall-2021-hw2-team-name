from __future__ import unicode_literals

from datetime import timedelta

from django.apps import apps
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.settings import settings_db_sync_task_delay

from .events import event_parsing_document_version_submit
from .tasks import task_parse_document_version


def method_document_get_content(self):
    latest_version = self.latest_version

    if latest_version:
        return latest_version.get_content()


method_document_get_content.help_text = _(
    'Return the parsed content of the document.'
)
method_document_get_content.short_description = _(
    'get_content()'
)


def method_document_page_get_content(self):
    DocumentPageContent = apps.get_model(
        app_label='document_parsing', model_name='DocumentPageContent'
    )

    try:
        page_content = self.content.content
    except DocumentPageContent.DoesNotExist:
        return ''
    else:
        return page_content


def method_document_submit_for_parsing(self, _user=None):
    latest_version = self.latest_version
    # Don't error out if document has no version
    if latest_version:
        latest_version.submit_for_parsing(_user=_user)


def method_document_version_get_content(self):
    result = []
    for page in self.pages.all():
        result.append(page.get_content())

    return ''.join(result)


method_document_version_get_content.help_text = _(
    'Return the parsed content of the document version.'
)


def method_document_version_submit_for_parsing(self, _user=None):
    event_parsing_document_version_submit.commit(
        action_object=self.document, actor=_user, target=self
    )

    task_parse_document_version.apply_async(
        eta=now() + timedelta(seconds=settings_db_sync_task_delay.value),
        kwargs={'document_version_pk': self.pk},
    )

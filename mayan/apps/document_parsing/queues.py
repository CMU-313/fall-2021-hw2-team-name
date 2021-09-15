from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.task_manager.classes import CeleryQueue

queue_ocr = CeleryQueue(label=_('Parsing'), name='parsing')

queue_ocr.add_task_type(
    label=_('Document version parsing'),
    name='mayan.apps.document_parsing.tasks.task_parse_document_version'
)

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.task_manager.classes import CeleryQueue

queue_ocr = CeleryQueue(label=_('OCR'), name='ocr')

queue_ocr.add_task_type(
    label=_('Document version OCR'), name='mayan.apps.ocr.tasks.task_do_ocr'
)

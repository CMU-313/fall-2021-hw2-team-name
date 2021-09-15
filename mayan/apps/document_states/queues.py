from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.task_manager.classes import CeleryQueue

queue_document_states = CeleryQueue(
    name='document_states', label=_('Document states')
)
queue_document_states_fast = CeleryQueue(
    name='document_states_fast', label=_('Document states fast')
)

queue_document_states.add_task_type(
    name='mayan.apps.document_states.tasks.task_launch_all_workflows',
    label=_('Launch all workflows')
)
queue_document_states_fast.add_task_type(
    name='mayan.apps.document_states.tasks.task_generate_document_state_image',
    label=_('Generate workflow previews')
)

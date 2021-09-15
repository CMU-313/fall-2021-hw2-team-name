from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.classes import ErrorLogNamespace

error_log_state_actions = ErrorLogNamespace(
    label=_('Workflow state actions'), name='workflow_state_actions'
)

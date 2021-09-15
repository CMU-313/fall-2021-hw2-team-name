from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _


def method_get_workflow(self, name):
    return self.workflows.get(workflow__internal_name=name)


method_get_workflow.short_description = _(
    'get_workflow(< workflow internal name >)'
)
method_get_workflow.help_text = _(
    'Return the current state of the selected workflow.'
)

from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(label=_('Document workflows'), name='document_states')

permission_workflow_create = namespace.add_permission(
    label=_('Create workflows'), name='workflow_create'
)
permission_workflow_delete = namespace.add_permission(
    label=_('Delete workflows'), name='workflow_delte'
)
permission_workflow_edit = namespace.add_permission(
    label=_('Edit workflows'), name='workflow_edit'
)
permission_workflow_view = namespace.add_permission(
    label=_('View workflows'), name='workflow_view'
)
# Translators: This text refers to the permission to grant user the ability to
# 'transition workflows' from one state to another, to move the workflow
# forwards
permission_workflow_transition = namespace.add_permission(
    label=_('Transition workflows'), name='workflow_transition'
)
permission_workflow_tools = namespace.add_permission(
    label=_('Execute workflow tools'), name='workflow_tools'
)

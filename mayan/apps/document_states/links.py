from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.icons import icon_document_type
from mayan.apps.navigation import Link


from .icons import (
    icon_document_workflow_instance_list, icon_tool_launch_all_workflows,
    icon_workflow_create, icon_workflow_delete, icon_workflow_edit,
    icon_workflow_list, icon_workflow_preview,
    icon_workflow_runtime_proxy_document_list, icon_workflow_runtime_proxy_list,
    icon_workflow_runtime_proxy_state_document_list,
    icon_workflow_runtime_proxy_state_list, icon_workflow_state,
    icon_workflow_state_action_delete, icon_workflow_state_action_edit,
    icon_workflow_state_action_list, icon_workflow_state_action_selection,
    icon_workflow_state_create, icon_workflow_state_delete,
    icon_workflow_state_edit, icon_workflow_transition,
    icon_workflow_transition_create, icon_workflow_transition_delete,
    icon_workflow_transition_edit, icon_workflow_transition_triggers
)
from .permissions import (
    permission_workflow_create, permission_workflow_delete,
    permission_workflow_edit, permission_workflow_tools,
    permission_workflow_view
)

link_document_workflow_instance_list = Link(
    icon_class=icon_document_workflow_instance_list,
    kwargs={'document_id': 'resolved_object.pk'},
    permission=permission_workflow_view, text=_('Workflows'),
    view='workflows:document_workflow_instance_list'
)
link_tool_launch_all_workflows = Link(
    icon_class=icon_tool_launch_all_workflows,
    permission=permission_workflow_tools, text=_('Launch all workflows'),
    view='workflows:tool_launch_all_workflows'
)
link_workflow_create = Link(
    icon_class=icon_workflow_create, permission=permission_workflow_create,
    text=_('Create workflow'), view='workflows:workflow_create'
)
link_workflow_delete = Link(
    icon_class=icon_workflow_delete,
    kwargs={'workflow_id': 'resolved_object.pk'},
    permission=permission_workflow_delete, tags='dangerous', text=_('Delete'),
    view='workflows:workflow_delete'
)
link_workflow_document_types = Link(
    icon_class=icon_document_type, kwargs={'workflow_id': 'resolved_object.pk'},
    permission=permission_workflow_edit, text=_('Document types'),
    view='workflows:workflow_document_types'
)
link_workflow_edit = Link(
    icon_class=icon_workflow_edit, kwargs={'workflow_id': 'resolved_object.pk'},
    permission=permission_workflow_edit, text=_('Edit'),
    view='workflows:workflow_edit'
)
link_workflow_list = Link(
    icon_class=icon_workflow_list, permission=permission_workflow_view,
    text=_('Workflows'), view='workflows:workflow_list'
)
link_workflow_preview = Link(
    icon_class=icon_workflow_preview,
    kwargs={'workflow_id': 'resolved_object.pk'},
    permission=permission_workflow_view, text=_('Preview'),
    view='workflows:workflow_preview'
)

# Workflow instances

link_workflow_instance_detail = Link(
    kwargs={'workflow_instance_id': 'resolved_object.pk'},
    permission=permission_workflow_view, text=_('Detail'),
    view='workflows:workflow_instance_detail'
)
link_workflow_instance_transition = Link(
    kwargs={'workflow_instance_id': 'resolved_object.pk'}, text=_('Transition'),
    view='workflows:workflow_instance_transition'
)

# Workflow state actions

link_workflow_state_action_delete = Link(
    icon_class=icon_workflow_state_action_delete,
    kwargs={'workflow_state_action_id': 'resolved_object.pk'},
    permission=permission_workflow_edit, tags='dangerous',
    text=_('Delete'), view='workflows:workflow_state_action_delete'
)
link_workflow_state_action_edit = Link(
    icon_class=icon_workflow_state_action_edit,
    kwargs={'workflow_state_action_id': 'resolved_object.pk'},
    permission=permission_workflow_edit, text=_('Edit'),
    view='workflows:workflow_state_action_edit'
)
link_workflow_state_action_list = Link(
    icon_class=icon_workflow_state_action_list,
    kwargs={'workflow_state_id': 'resolved_object.pk'},
    permission=permission_workflow_edit, text=_('Actions'),
    view='workflows:workflow_state_action_list'
)
link_workflow_state_action_selection = Link(
    icon_class=icon_workflow_state_action_selection,
    kwargs={'workflow_state_id': 'resolved_object.pk'},
    permission=permission_workflow_edit, text=_('Create action'),
    view='workflows:workflow_state_action_selection'
)

# Workflow states

link_workflow_state_create = Link(
    icon_class=icon_workflow_state_create,
    kwargs={'workflow_id': 'resolved_object.pk'},
    permission=permission_workflow_edit, text=_('Create state'),
    view='workflows:workflow_state_create'
)
link_workflow_state_delete = Link(
    icon_class=icon_workflow_state_delete,
    kwargs={'workflow_state_id': 'object.pk'},
    permission=permission_workflow_edit, tags='dangerous', text=_('Delete'),
    view='workflows:workflow_state_delete'
)
link_workflow_state_edit = Link(
    icon_class=icon_workflow_state_edit,
    kwargs={'workflow_state_id': 'resolved_object.pk'},
    permission=permission_workflow_edit, text=_('Edit'),
    view='workflows:workflow_state_edit'
)
link_workflow_state_list = Link(
    icon_class=icon_workflow_state,
    kwargs={'workflow_id': 'resolved_object.pk'},
    permission=permission_workflow_view, text=_('States'),
    view='workflows:workflow_state_list'
)

# Workflow transitions

link_workflow_transition_create = Link(
    icon_class=icon_workflow_transition_create,
    kwargs={'workflow_id': 'resolved_object.pk'},
    permission=permission_workflow_edit, text=_('Create transition'),
    view='workflows:workflow_transition_create'
)
link_workflow_transition_delete = Link(
    icon_class=icon_workflow_transition_delete,
    kwargs={'workflow_transition_id': 'resolved_object.pk'},
    permission=permission_workflow_edit, tags='dangerous', text=_('Delete'),
    view='workflows:workflow_transition_delete'
)
link_workflow_transition_edit = Link(
    icon_class=icon_workflow_transition_edit,
    kwargs={'workflow_transition_id': 'resolved_object.pk'},
    permission=permission_workflow_edit, text=_('Edit'),
    view='workflows:workflow_transition_edit'
)
link_workflow_transition_list = Link(
    icon_class=icon_workflow_transition,
    kwargs={'workflow_id': 'resolved_object.pk'},
    permission=permission_workflow_view, text=_('Transitions'),
    view='workflows:workflow_transition_list'
)
link_workflow_transition_triggers = Link(
    icon_class=icon_workflow_transition_triggers,
    kwargs={'workflow_transition_id': 'resolved_object.pk'},
    permission=permission_workflow_edit, text=_('Transition triggers'),
    view='workflows:workflow_transition_triggers'
)

# Workflow runtime proxies

link_workflow_runtime_proxy_document_list = Link(
    icon_class=icon_workflow_runtime_proxy_document_list,
    kwargs={'workflow_runtime_proxy_id': 'resolved_object.pk'},
    permission=permission_workflow_view, text=_('Workflow documents'),
    view='workflows:workflow_runtime_proxy_document_list'
)
link_workflow_runtime_proxy_list = Link(
    icon_class=icon_workflow_runtime_proxy_list,
    permission=permission_workflow_view, text=_('Workflows'),
    view='workflows:workflow_runtime_proxy_list'
)
link_workflow_runtime_proxy_state_document_list = Link(
    icon_class=icon_workflow_runtime_proxy_state_document_list,
    kwargs={'workflow_runtime_proxy_state_id': 'resolved_object.pk'},
    permission=permission_workflow_view, text=_('State documents'),
    view='workflows:workflow_runtime_proxy_state_document_list'
)
link_workflow_runtime_proxy_state_list = Link(
    icon_class=icon_workflow_runtime_proxy_state_list,
    kwargs={'workflow_runtime_proxy_id': 'resolved_object.pk'},
    permission=permission_workflow_view, text=_('States'),
    view='workflows:workflow_runtime_proxy_state_list'
)

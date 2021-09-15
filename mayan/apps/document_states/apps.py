from __future__ import unicode_literals

from django.apps import apps
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from kombu import Exchange, Queue

from mayan.apps.acls import ModelPermission
from mayan.apps.acls.links import link_acl_list
from mayan.apps.common import (
    MayanAppConfig, menu_facet, menu_list_facet, menu_main, menu_object,
    menu_secondary, menu_setup, menu_sidebar, menu_tools
)
from mayan.apps.common.classes import ModelAttribute
from mayan.apps.common.links import link_object_error_list
from mayan.apps.common.permissions_runtime import permission_error_log_view
from mayan.apps.common.widgets import TwoStateWidget
from mayan.apps.navigation import SourceColumn
from mayan.celery import app

from .classes import WorkflowAction
from .handlers import (
    handler_index_document, handler_launch_workflow,
    handler_trigger_transition,
)
from .methods import method_get_workflow
from .links import (
    link_document_workflow_instance_list, link_setup_workflow_create,
    link_setup_workflow_delete, link_setup_workflow_document_types,
    link_setup_workflow_edit, link_setup_workflow_list,
    link_setup_workflow_state_action_delete,
    link_setup_workflow_state_action_edit,
    link_setup_workflow_state_action_list,
    link_setup_workflow_state_action_selection,
    link_setup_workflow_state_create, link_setup_workflow_state_delete,
    link_setup_workflow_state_edit, link_setup_workflow_states,
    link_setup_workflow_transition_create,
    link_setup_workflow_transition_delete, link_setup_workflow_transition_edit,
    link_setup_workflow_transitions, link_tool_launch_all_workflows,
    link_workflow_document_list, link_workflow_instance_detail,
    link_workflow_instance_transition,
    link_workflow_instance_transition_events, link_workflow_list,
    link_workflow_preview, link_workflow_state_document_list,
    link_workflow_state_list
)
from .permissions import (
    permission_workflow_delete, permission_workflow_edit,
    permission_workflow_transition, permission_workflow_view
)
from .queues import *  # NOQA
from .widgets import widget_transition_events


class DocumentStatesApp(MayanAppConfig):
    app_namespace = 'document_states'
    app_url = 'workflows'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.document_states'
    verbose_name = _('Workflows')

    def ready(self):
        super(DocumentStatesApp, self).ready()

        Action = apps.get_model(
            app_label='actstream', model_name='Action'
        )
        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )
        ErrorLogEntry = apps.get_model(
            app_label='common', model_name='ErrorLogEntry'
        )

        Workflow = self.get_model('Workflow')
        WorkflowInstance = self.get_model('WorkflowInstance')
        WorkflowInstanceLogEntry = self.get_model('WorkflowInstanceLogEntry')
        WorkflowRuntimeProxy = self.get_model('WorkflowRuntimeProxy')
        WorkflowState = self.get_model('WorkflowState')
        WorkflowStateAction = self.get_model('WorkflowStateAction')
        WorkflowStateRuntimeProxy = self.get_model('WorkflowStateRuntimeProxy')
        WorkflowTransition = self.get_model('WorkflowTransition')
        WorkflowTransitionTriggerEvent = self.get_model(
            'WorkflowTransitionTriggerEvent'
        )

        Document.add_to_class(
            name='get_workflow', value=method_get_workflow
        )

        ErrorLogEntry.objects.register(model=WorkflowStateAction)

        WorkflowAction.initialize()

        ModelAttribute(model=Document, name='get_workflow')

        ModelPermission.register(
            model=Document, permissions=(permission_workflow_view,)
        )
        ModelPermission.register(
            model=Workflow, permissions=(
                permission_error_log_view, permission_workflow_delete,
                permission_workflow_edit, permission_workflow_transition,
                permission_workflow_view,
            )
        )

        ModelPermission.register_inheritance(
            model=WorkflowInstance, related='workflow',
        )
        ModelPermission.register_inheritance(
            model=WorkflowInstanceLogEntry,
            related='workflow_instance__workflow',
        )
        ModelPermission.register(
            model=WorkflowTransition,
            permissions=(permission_workflow_transition,)
        )

        ModelPermission.register_inheritance(
            model=WorkflowState, related='workflow',
        )
        ModelPermission.register_inheritance(
            model=WorkflowStateAction, related='state__workflow',
        )
        ModelPermission.register_inheritance(
            model=WorkflowTransition, related='workflow',
        )
        ModelPermission.register_inheritance(
            model=WorkflowTransitionTriggerEvent,
            related='transition__workflow',
        )

        SourceColumn(
            attribute='label', is_identifier=True, source=Workflow
        )
        SourceColumn(attribute='internal_name', source=Workflow)
        SourceColumn(attribute='get_initial_state', source=Workflow)

        SourceColumn(
            attribute='workflow', is_identifier=True,
            source=WorkflowInstance
        )
        SourceColumn(attribute='get_current_state', source=WorkflowInstance)
        SourceColumn(
            attribute='get_last_transition_user', source=WorkflowInstance
        )
        SourceColumn(
            attribute='get_last_transition', source=WorkflowInstance
        )
        SourceColumn(
            attribute='get_last_transition_datetime', kwargs={
                'formatted': True
            }, source=WorkflowInstance
        )
        SourceColumn(
            attribute='get_current_completion', source=WorkflowInstance
        )

        SourceColumn(
            attribute='get_rendered_datetime', source=WorkflowInstanceLogEntry
        )
        SourceColumn(attribute='user', source=WorkflowInstanceLogEntry)
        SourceColumn(attribute='transition', source=WorkflowInstanceLogEntry)
        SourceColumn(attribute='comment', source=WorkflowInstanceLogEntry)

        SourceColumn(
            attribute='label', is_identifier=True, source=WorkflowState
        )
        SourceColumn(
            attribute='initial', source=WorkflowState, widget=TwoStateWidget
        )
        SourceColumn(attribute='completion', source=WorkflowState)

        SourceColumn(
            attribute='label', is_identifier=True, source=WorkflowStateAction
        )
        SourceColumn(
            attribute='enabled', source=WorkflowStateAction,
            widget=TwoStateWidget
        )
        SourceColumn(
            attribute='get_when_display', label=_('When?'),
            source=WorkflowStateAction
        )
        SourceColumn(attribute='get_class_label', source=WorkflowStateAction)

        SourceColumn(
            attribute='label', is_identifier=True, source=WorkflowTransition
        )
        SourceColumn(attribute='origin_state', source=WorkflowTransition)
        SourceColumn(attribute='destination_state', source=WorkflowTransition)
        SourceColumn(
            func=lambda context: widget_transition_events(
                transition=context['object']
            ), label=_('Triggers'), source=WorkflowTransition
        )

        app.conf.task_queues.extend(
            (
                Queue(
                    'document_states', Exchange('document_states'),
                    routing_key='document_states'
                ),
            )
        )

        app.conf.task_queues.extend(
            (
                Queue(
                    'document_states_fast', Exchange('document_states_fast'),
                    routing_key='document_states_fast'
                ),
            )
        )

        app.conf.task_routes.update(
            {
                'mayan.apps.document_states.tasks.task_generate_document_state_image': {
                    'queue': 'document_states'
                },
                'mayan.apps.document_states.tasks.task_launch_all_workflows': {
                    'queue': 'document_states_fast'
                },
            }
        )

        menu_facet.bind_links(
            links=(link_document_workflow_instance_list,), sources=(Document,)
        )
        menu_list_facet.bind_links(
            links=(
                link_setup_workflow_document_types,
                link_setup_workflow_states, link_setup_workflow_transitions,
                link_workflow_preview, link_acl_list
            ), sources=(Workflow,)
        )
        menu_main.bind_links(links=(link_workflow_list,), position=10)
        menu_object.bind_links(
            links=(
                link_setup_workflow_edit,
                link_setup_workflow_delete
            ), sources=(Workflow,)
        )
        menu_object.bind_links(
            links=(
                link_setup_workflow_state_edit,
                link_setup_workflow_state_action_list,
                link_setup_workflow_state_delete
            ), sources=(WorkflowState,)
        )
        menu_object.bind_links(
            links=(
                link_setup_workflow_transition_edit,
                link_workflow_instance_transition_events, link_acl_list,
                link_setup_workflow_transition_delete
            ), sources=(WorkflowTransition,)
        )
        menu_object.bind_links(
            links=(
                link_workflow_instance_detail,
                link_workflow_instance_transition
            ), sources=(WorkflowInstance,)
        )
        menu_object.bind_links(
            links=(
                link_workflow_document_list, link_workflow_state_list,
            ), sources=(WorkflowRuntimeProxy,)
        )
        menu_object.bind_links(
            links=(
                link_workflow_state_document_list,
            ), sources=(WorkflowStateRuntimeProxy,)
        )
        menu_object.bind_links(
            links=(
                link_setup_workflow_state_action_edit,
                link_object_error_list,
                link_setup_workflow_state_action_delete,
            ), sources=(WorkflowStateAction,)
        )

        menu_secondary.bind_links(
            links=(link_setup_workflow_list, link_setup_workflow_create),
            sources=(
                Workflow, 'document_states:setup_workflow_create',
                'document_states:setup_workflow_list'
            )
        )
        menu_secondary.bind_links(
            links=(link_workflow_list,),
            sources=(
                WorkflowRuntimeProxy,
            )
        )
        menu_secondary.bind_links(
            links=(link_setup_workflow_state_action_selection,),
            sources=(
                WorkflowState,
            )
        )
        menu_setup.bind_links(links=(link_setup_workflow_list,))
        menu_sidebar.bind_links(
            links=(
                link_setup_workflow_transition_create,
            ), sources=(
                WorkflowTransition,
                'document_states:setup_workflow_transition_list',
            )
        )
        menu_sidebar.bind_links(
            links=(
                link_setup_workflow_state_create,
            ), sources=(
                WorkflowState,
                'document_states:setup_workflow_state_list',
            )
        )
        menu_tools.bind_links(links=(link_tool_launch_all_workflows,))

        post_save.connect(
            dispatch_uid='workflows_handler_launch_workflow',
            receiver=handler_launch_workflow, sender=Document
        )

        # Index updating

        post_save.connect(
            dispatch_uid='workflows_handler_index_document_save',
            receiver=handler_index_document, sender=WorkflowInstanceLogEntry
        )
        post_save.connect(
            dispatch_uid='workflows_handler_handler_trigger_transition',
            receiver=handler_trigger_transition, sender=Action
        )

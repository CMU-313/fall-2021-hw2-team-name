from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.mixins import ExternalObjectMixin
from mayan.apps.common.generics import (
    AssignRemoveView, ConfirmView, FormView, SingleObjectCreateView,
    SingleObjectDeleteView, SingleObjectDetailView,
    SingleObjectDynamicFormCreateView, SingleObjectDynamicFormEditView,
    SingleObjectEditView, SingleObjectListView
)
from mayan.apps.events.classes import EventType
from mayan.apps.events.models import StoredEventType

from ..classes import WorkflowAction
from ..forms import (
    WorkflowActionSelectionForm, WorkflowForm, WorkflowPreviewForm,
    WorkflowStateActionDynamicForm, WorkflowStateForm, WorkflowTransitionForm,
    WorkflowTransitionTriggerEventRelationshipFormSet
)
from ..icons import (
    icon_workflow_list, icon_workflow_state, icon_workflow_state_action,
    icon_workflow_transition
)
from ..links import (
    link_workflow_create, link_workflow_state_action_selection,
    link_workflow_state_create, link_workflow_transition_create
)
from ..models import (
    Workflow, WorkflowState, WorkflowStateAction, WorkflowTransition
)
from ..permissions import (
    permission_workflow_create, permission_workflow_delete,
    permission_workflow_edit, permission_workflow_tools,
    permission_workflow_view
)
from ..tasks import task_launch_all_workflows

__all__ = (
    'ToolLaunchAllWorkflows', 'WorkflowCreateView', 'WorkflowDeleteView',
    'WorkflowDocumentTypesView', 'WorkflowEditView', 'WorkflowListView',
    'WorkflowPreviewView', 'WorkflowStateActionCreateView',
    'WorkflowStateActionDeleteView', 'WorkflowStateActionEditView',
    'WorkflowStateActionListView', 'WorkflowStateActionSelectionView',
    'WorkflowStateCreateView', 'WorkflowStateDeleteView',
    'WorkflowStateEditView', 'WorkflowStateListView',
    'WorkflowTransitionCreateView', 'WorkflowTransitionDeleteView',
    'WorkflowTransitionEditView', 'WorkflowTransitionListView',
    'WorkflowTransitionTriggerEventListView'
)


class ToolLaunchAllWorkflows(ConfirmView):
    extra_context = {
        'title': _('Launch all workflows?'),
        'subtitle': _(
            'This will launch all workflows created after documents have '
            'already been uploaded.'
        )
    }
    view_permission = permission_workflow_tools

    def view_action(self):
        task_launch_all_workflows.apply_async()
        messages.success(
            message=_('Workflow launch queued successfully.'),
            request=self.request
        )


class WorkflowCreateView(SingleObjectCreateView):
    extra_context = {
        'title': _('Create new workflow'),
    }
    form_class = WorkflowForm
    model = Workflow
    post_action_redirect = reverse_lazy(viewname='workflows:workflow_list')
    view_permission = permission_workflow_create


class WorkflowDeleteView(SingleObjectDeleteView):
    model = Workflow
    object_permission = permission_workflow_delete
    pk_url_kwarg = 'workflow_id'
    post_action_redirect = reverse_lazy(viewname='workflows:workflow_list')


class WorkflowDocumentTypesView(AssignRemoveView):
    decode_content_type = True
    left_list_title = _('Available document types')
    object_permission = permission_workflow_edit
    right_list_title = _('Document types assigned this workflow')

    def add(self, item):
        self.get_object().document_types.add(item)
        # TODO: add task launching this workflow for all the document types
        # of item

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'subtitle': _(
                'Removing a document type from a workflow will also '
                'remove all running instances of that workflow for '
                'documents of the document type just removed.'
            ),
            'title': _(
                'Document types assigned the workflow: %s'
            ) % self.get_object(),
        }

    def get_object(self):
        return get_object_or_404(
            klass=Workflow, pk=self.kwargs['workflow_id']
        )

    def left_list(self):
        return AssignRemoveView.generate_choices(
            self.get_object().get_document_types_not_in_workflow()
        )

    def right_list(self):
        return AssignRemoveView.generate_choices(
            self.get_object().document_types.all()
        )

    def remove(self, item):
        # When removing a document type to workflow association
        # also remove all running workflows in documents of that type.
        with transaction.atomic():
            self.get_object().document_types.remove(item)
            self.get_object().instances.filter(document__document_type=item).delete()


class WorkflowEditView(SingleObjectEditView):
    form_class = WorkflowForm
    model = Workflow
    object_permission = permission_workflow_edit
    pk_url_kwarg = 'workflow_id'
    post_action_redirect = reverse_lazy(viewname='workflows:workflow_list')


class WorkflowListView(SingleObjectListView):
    model = Workflow
    object_permission = permission_workflow_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_workflow_list,
            'no_results_main_link': link_workflow_create.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'Workflows store a series of states and keep track of the '
                'current state of a document. Transitions are used to change the '
                'current state to a new one.'
            ),
            'no_results_title': _(
                'No workflows have been defined'
            ),
            'title': _('Workflows'),
        }


class WorkflowPreviewView(SingleObjectDetailView):
    form_class = WorkflowPreviewForm
    model = Workflow
    object_permission = permission_workflow_view
    pk_url_kwarg = 'workflow_id'

    def get_extra_context(self):
        return {
            'hide_labels': True,
            'object': self.get_object(),
            'title': _('Preview of: %s') % self.get_object()
        }


class WorkflowStateActionCreateView(SingleObjectDynamicFormCreateView):
    form_class = WorkflowStateActionDynamicForm
    object_permission = permission_workflow_edit

    def get_class(self):
        try:
            return WorkflowAction.get(name=self.kwargs['class_path'])
        except KeyError:
            raise Http404(
                '{} class not found'.format(self.kwargs['class_path'])
            )

    def get_extra_context(self):
        return {
            'navigation_object_list': ('object', 'workflow'),
            'object': self.get_object(),
            'title': _(
                'Create a "%s" workflow action'
            ) % self.get_class().label,
            'workflow': self.get_object().workflow
        }

    def get_form_extra_kwargs(self):
        return {
            'request': self.request,
            'action_path': self.kwargs['class_path']
        }

    def get_form_schema(self):
        return self.get_class()().get_form_schema(request=self.request)

    def get_instance_extra_data(self):
        return {
            'action_path': self.kwargs['class_path'],
            'state': self.get_object()
        }

    def get_object(self):
        return get_object_or_404(
            klass=WorkflowState, pk=self.kwargs['workflow_state_id']
        )

    def get_post_action_redirect(self):
        return reverse(
            viewname='workflows:workflow_state_action_list',
            kwargs={'workflow_state_id': self.get_object().pk}
        )


class WorkflowStateActionDeleteView(SingleObjectDeleteView):
    model = WorkflowStateAction
    object_permission = permission_workflow_edit
    pk_url_kwarg = 'workflow_state_action_id'

    def get_extra_context(self):
        return {
            'navigation_object_list': (
                'object', 'workflow_state', 'workflow'
            ),
            'object': self.get_object(),
            'title': _('Delete workflow state action: %s') % self.get_object(),
            'workflow': self.get_object().state.workflow,
            'workflow_state': self.get_object().state,
        }

    def get_post_action_redirect(self):
        return reverse(
            viewname='workflows:workflow_state_action_list',
            kwargs={'workflow_state_id': self.get_object().state.pk}
        )


class WorkflowStateActionEditView(SingleObjectDynamicFormEditView):
    form_class = WorkflowStateActionDynamicForm
    model = WorkflowStateAction
    object_permission = permission_workflow_edit
    pk_url_kwarg = 'workflow_state_action_id'

    def get_extra_context(self):
        return {
            'navigation_object_list': (
                'object', 'workflow_state', 'workflow'
            ),
            'object': self.get_object(),
            'title': _('Edit workflow state action: %s') % self.get_object(),
            'workflow': self.get_object().state.workflow,
            'workflow_state': self.get_object().state,
        }

    def get_form_extra_kwargs(self):
        return {
            'request': self.request,
            'action_path': self.get_object().action_path,
        }

    def get_form_schema(self):
        return self.get_object().get_class_instance().get_form_schema(
            request=self.request
        )

    def get_post_action_redirect(self):
        return reverse(
            viewname='workflows:workflow_state_action_list',
            kwargs={'workflow_state_id': self.get_object().state.pk}
        )


class WorkflowStateActionListView(SingleObjectListView):
    object_permission = permission_workflow_edit

    def get_extra_context(self):
        return {
            'hide_object': True,
            'navigation_object_list': ('object', 'workflow'),
            'no_results_icon': icon_workflow_state_action,
            'no_results_main_link': link_workflow_state_action_selection.resolve(
                context=RequestContext(
                    request=self.request, dict_={
                        'object': self.get_workflow_state()
                    }
                )
            ),
            'no_results_text': _(
                'Workflow state actions are macros that get executed when '
                'documents enters or leaves the state in which they reside.'
            ),
            'no_results_title': _(
                'There are no actions for this workflow state'
            ),
            'object': self.get_workflow_state(),
            'title': _(
                'Actions for workflow state: %s'
            ) % self.get_workflow_state(),
            'workflow': self.get_workflow_state().workflow,
        }

    def get_form_schema(self):
        return {'fields': self.get_class().fields}

    def get_source_queryset(self):
        return self.get_workflow_state().actions.all()

    def get_workflow_state(self):
        return get_object_or_404(
            klass=WorkflowState, pk=self.kwargs['workflow_state_id']
        )


class WorkflowStateActionSelectionView(FormView):
    form_class = WorkflowActionSelectionForm
    view_permission = permission_workflow_edit

    def form_valid(self, form):
        klass = form.cleaned_data['klass']
        return HttpResponseRedirect(
            redirect_to=reverse(
                viewname='workflows:workflow_state_action_create',
                kwargs={
                    'workflow_state_id': self.get_object().pk,
                    'class_path': klass
                }
            )
        )

    def get_extra_context(self):
        return {
            'navigation_object_list': (
                'object', 'workflow'
            ),
            'object': self.get_object(),
            'title': _('New workflow state action selection'),
            'workflow': self.get_object().workflow,
        }

    def get_object(self):
        return get_object_or_404(
            klass=WorkflowState, pk=self.kwargs['workflow_state_id']
        )


class WorkflowStateCreateView(ExternalObjectMixin, SingleObjectCreateView):
    external_object_class = Workflow
    external_object_permission = permission_workflow_edit
    external_object_pk_url_kwarg = 'workflow_id'
    form_class = WorkflowStateForm

    def get_extra_context(self):
        return {
            'object': self.get_workflow(),
            'title': _(
                'Create states for workflow: %s'
            ) % self.get_workflow()
        }

    def get_instance_extra_data(self):
        return {'workflow': self.get_workflow()}

    def get_source_queryset(self):
        return self.get_workflow().states.all()

    def get_success_url(self):
        return reverse(
            viewname='workflows:workflow_state_list',
            kwargs={'workflow_id': self.kwargs['workflow_id']}
        )

    def get_workflow(self):
        return self.get_external_object()


class WorkflowStateDeleteView(SingleObjectDeleteView):
    model = WorkflowState
    object_permission = permission_workflow_edit
    pk_url_kwarg = 'workflow_state_id'

    def get_extra_context(self):
        return {
            'navigation_object_list': ('object', 'workflow_instance'),
            'object': self.get_object(),
            'workflow_instance': self.get_object().workflow,
        }

    def get_success_url(self):
        return reverse(
            viewname='workflows:workflow_state_list',
            kwargs={'workflow_id': self.get_object().workflow.pk}
        )


class WorkflowStateEditView(SingleObjectEditView):
    form_class = WorkflowStateForm
    model = WorkflowState
    object_permission = permission_workflow_edit
    pk_url_kwarg = 'workflow_state_id'

    def get_extra_context(self):
        return {
            'navigation_object_list': ('object', 'workflow_instance'),
            'object': self.get_object(),
            'workflow_instance': self.get_object().workflow,
        }

    def get_success_url(self):
        return reverse(
            viewname='workflows:workflow_state_list',
            kwargs={'workflow_id': self.get_object().workflow.pk}
        )


class WorkflowStateListView(ExternalObjectMixin, SingleObjectListView):
    external_object_class = Workflow
    external_object_permission = permission_workflow_view
    external_object_pk_url_kwarg = 'workflow_id'
    object_permission = permission_workflow_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_workflow_state,
            'no_results_main_link': link_workflow_state_create.resolve(
                context=RequestContext(
                    self.request, {'object': self.get_workflow()}
                )
            ),
            'no_results_text': _(
                'Create states and link them using transitions.'
            ),
            'no_results_title': _(
                'This workflow doesn\'t have any states'
            ),
            'object': self.get_workflow(),
            'title': _('States of workflow: %s') % self.get_workflow()
        }

    def get_source_queryset(self):
        return self.get_workflow().states.all()

    def get_workflow(self):
        return self.get_external_object()


class WorkflowTransitionCreateView(ExternalObjectMixin, SingleObjectCreateView):
    external_object_class = Workflow
    external_object_permission = permission_workflow_edit
    external_object_pk_url_kwarg = 'workflow_id'
    form_class = WorkflowTransitionForm

    def get_extra_context(self):
        return {
            'object': self.get_workflow(),
            'title': _(
                'Create transitions for workflow: %s'
            ) % self.get_workflow()
        }

    def get_form_kwargs(self):
        kwargs = super(
            WorkflowTransitionCreateView, self
        ).get_form_kwargs()
        kwargs['workflow'] = self.get_workflow()
        return kwargs

    def get_instance_extra_data(self):
        return {'workflow': self.get_workflow()}

    def get_source_queryset(self):
        return self.get_workflow().transitions.all()

    def get_success_url(self):
        return reverse(
            viewname='workflows:workflow_transition_list',
            kwargs={'workflow_id': self.kwargs['workflow_id']}
        )

    def get_workflow(self):
        return self.get_external_object()


class WorkflowTransitionDeleteView(SingleObjectDeleteView):
    model = WorkflowTransition
    object_permission = permission_workflow_edit
    pk_url_kwarg = 'workflow_transition_id'

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'navigation_object_list': ('object', 'workflow_instance'),
            'workflow_instance': self.get_object().workflow,
        }

    def get_success_url(self):
        return reverse(
            viewname='workflows:workflow_transition_list',
            kwargs={'workflow_id': self.get_object().workflow.pk}
        )


class WorkflowTransitionEditView(SingleObjectEditView):
    form_class = WorkflowTransitionForm
    model = WorkflowTransition
    object_permission = permission_workflow_edit
    pk_url_kwarg = 'workflow_transition_id'

    def get_extra_context(self):
        return {
            'navigation_object_list': ('object', 'workflow_instance'),
            'object': self.get_object(),
            'workflow_instance': self.get_object().workflow,
        }

    def get_form_kwargs(self):
        kwargs = super(
            WorkflowTransitionEditView, self
        ).get_form_kwargs()
        kwargs['workflow'] = self.get_object().workflow
        return kwargs

    def get_success_url(self):
        return reverse(
            viewname='workflows:workflow_transition_list',
            kwargs={'workflow_id': self.get_object().workflow.pk}
        )


class WorkflowTransitionListView(ExternalObjectMixin, SingleObjectListView):
    external_object_class = Workflow
    external_object_permission = permission_workflow_view
    external_object_pk_url_kwarg = 'workflow_id'
    object_permission = permission_workflow_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_workflow_transition,
            'no_results_main_link': link_workflow_transition_create.resolve(
                context=RequestContext(
                    self.request, {'object': self.get_workflow()}
                )
            ),
            'no_results_text': _(
                'Create a transition and use it to move a workflow from '
                ' one state to another.'
            ),
            'no_results_title': _(
                'This workflow doesn\'t have any transitions'
            ),
            'object': self.get_workflow(),
            'title': _(
                'Transitions of workflow: %s'
            ) % self.get_workflow()
        }

    def get_source_queryset(self):
        return self.get_workflow().transitions.all()

    def get_workflow(self):
        return self.get_external_object()


class WorkflowTransitionTriggerEventListView(ExternalObjectMixin, FormView):
    external_object_class = WorkflowTransition
    external_object_permission = permission_workflow_edit
    external_object_pk_url_kwarg = 'workflow_transition_id'
    form_class = WorkflowTransitionTriggerEventRelationshipFormSet
    submodel = StoredEventType

    def dispatch(self, *args, **kwargs):
        EventType.refresh()
        return super(
            WorkflowTransitionTriggerEventListView, self
        ).dispatch(*args, **kwargs)

    def form_valid(self, form):
        try:
            for instance in form:
                instance.save()
        except Exception as exception:
            messages.error(
                message=_(
                    'Error updating workflow transition trigger events; %s'
                ) % exception, request=self.request

            )
        else:
            messages.success(
                message=_(
                    'Workflow transition trigger events updated successfully'
                ), request=self.request
            )

        return super(
            WorkflowTransitionTriggerEventListView, self
        ).form_valid(form=form)

    def get_object(self):
        return self.get_external_object()

    def get_extra_context(self):
        return {
            'form_display_mode_table': True,
            'navigation_object_list': ('object', 'workflow'),
            'object': self.get_object(),
            'subtitle': _(
                'Triggers are events that cause this transition to execute '
                'automatically.'
            ),
            'title': _(
                'Workflow transition trigger events for: %s'
            ) % self.get_object(),
            'workflow': self.get_object().workflow,
        }

    def get_initial(self):
        obj = self.get_object()
        initial = []

        # Return the queryset by name from the sorted list of the class
        event_type_ids = [event_type.id for event_type in EventType.all()]
        event_type_queryset = StoredEventType.objects.filter(
            name__in=event_type_ids
        )

        for event_type in event_type_queryset:
            initial.append({
                'transition': obj,
                'event_type': event_type,
            })
        return initial

    def get_post_action_redirect(self):
        return reverse(
            viewname='workflows:workflow_transition_list',
            kwargs={'workflow_id': self.get_object().workflow.pk}
        )

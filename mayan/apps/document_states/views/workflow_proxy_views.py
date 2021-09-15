from __future__ import absolute_import, unicode_literals

from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.mixins import ExternalObjectMixin
from mayan.apps.common.generics import SingleObjectListView
from mayan.apps.documents.models import Document
from mayan.apps.documents.views import DocumentListView

from ..icons import icon_workflow_list
from ..links import link_workflow_create, link_workflow_state_create
from ..models import WorkflowRuntimeProxy, WorkflowStateRuntimeProxy
from ..permissions import permission_workflow_view

__all__ = (
    'WorkflowRuntimeProxyDocumentListView', 'WorkflowRuntimeProxyListView',
    'WorkflowRuntimeProxyStateDocumentListView',
    'WorkflowRuntimeProxyStateListView'
)


class WorkflowRuntimeProxyDocumentListView(ExternalObjectMixin, DocumentListView):
    external_object_class = WorkflowRuntimeProxy
    external_object_permission = permission_workflow_view
    external_object_pk_url_kwarg = 'workflow_runtime_proxy_id'

    def get_document_queryset(self):
        return Document.objects.filter(workflows__workflow=self.get_workflow())

    def get_extra_context(self):
        context = super(WorkflowRuntimeProxyDocumentListView, self).get_extra_context()
        context.update(
            {
                'no_results_text': _(
                    'Associate a workflow with some document types and '
                    'documents of those types will be listed in this view.'
                ),
                'no_results_title': _(
                    'There are no documents executing this workflow'
                ),
                'object': self.get_workflow(),
                'title': _('Documents with the workflow: %s') % self.get_workflow()
            }
        )
        return context

    def get_workflow(self):
        return self.get_external_object()


class WorkflowRuntimeProxyListView(SingleObjectListView):
    object_permission = permission_workflow_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_workflow_list,
            'no_results_main_link': link_workflow_create.resolve(
                context=RequestContext(
                    self.request, {}
                )
            ),
            'no_results_text': _(
                'Create some workflows and associated them with a document '
                'type. Active workflows will be shown here and the documents '
                'for which they are executing.'
            ),
            'no_results_title': _('There are no workflows'),
            'title': _('Workflows'),
        }

    def get_source_queryset(self):
        return WorkflowRuntimeProxy.objects.all()


class WorkflowRuntimeProxyStateDocumentListView(ExternalObjectMixin, DocumentListView):
    external_object_class = WorkflowStateRuntimeProxy
    external_object_permission = permission_workflow_view
    external_object_pk_url_kwarg = 'workflow_runtime_proxy_state_id'

    def get_document_queryset(self):
        return self.get_workflow_state().get_documents()

    def get_extra_context(self):
        workflow_state = self.get_workflow_state()
        context = super(WorkflowRuntimeProxyStateDocumentListView, self).get_extra_context()
        context.update(
            {
                'object': workflow_state,
                'navigation_object_list': ('object', 'workflow'),
                'no_results_title': _(
                    'There are documents in this workflow state'
                ),
                'title': _(
                    'Documents in the workflow "%s", state "%s"'
                ) % (
                    workflow_state.workflow, workflow_state
                ),
                'workflow': WorkflowRuntimeProxy.objects.get(
                    pk=workflow_state.workflow.pk
                ),
            }
        )
        return context

    def get_workflow_state(self):
        return self.get_external_object()


class WorkflowRuntimeProxyStateListView(ExternalObjectMixin, SingleObjectListView):
    external_object_class = WorkflowRuntimeProxy
    external_object_permission = permission_workflow_view
    external_object_pk_url_kwarg = 'workflow_runtime_proxy_id'

    def get_extra_context(self):
        return {
            'hide_columns': True,
            'hide_link': True,
            'no_results_main_link': link_workflow_state_create.resolve(
                context=RequestContext(
                    self.request, {'object': self.get_workflow()}
                )
            ),
            'no_results_text': _(
                'Create states and link them using transitions.'
            ),
            'no_results_title': _(
                'This workflow doesn\'t have any state'
            ),
            'object': self.get_workflow(),
            'title': _('States of workflow: %s') % self.get_workflow()
        }

    def get_source_queryset(self):
        return WorkflowStateRuntimeProxy.objects.filter(
            workflow=self.get_workflow()
        )

    def get_workflow(self):
        return self.get_external_object()

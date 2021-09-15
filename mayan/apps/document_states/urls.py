from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    WorkflowAPIViewSet, WorkflowStateAPIViewSet,
    WorkflowTransitionAPIViewSet
)
from .views import (
    DocumentWorkflowInstanceListView, ToolLaunchAllWorkflows,
    WorkflowCreateView, WorkflowDeleteView, WorkflowDocumentTypesView,
    WorkflowEditView, WorkflowInstanceDetailView,
    WorkflowInstanceTransitionView, WorkflowListView, WorkflowPreviewView,
    WorkflowRuntimeProxyDocumentListView, WorkflowRuntimeProxyListView,
    WorkflowRuntimeProxyStateDocumentListView,
    WorkflowRuntimeProxyStateListView, WorkflowStateActionCreateView,
    WorkflowStateActionDeleteView, WorkflowStateActionEditView,
    WorkflowStateActionListView, WorkflowStateActionSelectionView,
    WorkflowStateCreateView, WorkflowStateDeleteView, WorkflowStateEditView,
    WorkflowStateListView, WorkflowTransitionCreateView,
    WorkflowTransitionDeleteView, WorkflowTransitionEditView,
    WorkflowTransitionListView, WorkflowTransitionTriggerEventListView
)

urlpatterns = [
    url(
        regex=r'^workflows/$', name='workflow_list',
        view=WorkflowListView.as_view()
    ),
    url(
        regex=r'^workflows/create/$', name='workflow_create',
        view=WorkflowCreateView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/delete/$',
        name='workflow_delete', view=WorkflowDeleteView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/edit/$',
        name='workflow_edit', view=WorkflowEditView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/preview/$',
        name='workflow_preview', view=WorkflowPreviewView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/document_types/$',
        name='workflow_document_types',
        view=WorkflowDocumentTypesView.as_view()
    ),

    # Workflow states

    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/states/$',
        name='workflow_state_list',
        view=WorkflowStateListView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/states/create/$',
        name='workflow_state_create',
        view=WorkflowStateCreateView.as_view()
    ),
    url(
        regex=r'^workflows/states/(?P<workflow_state_id>\d+)/delete/$',
        name='workflow_state_delete',
        view=WorkflowStateDeleteView.as_view()
    ),
    url(
        regex=r'^workflows/states/(?P<workflow_state_id>\d+)/edit/$',
        name='workflow_state_edit',
        view=WorkflowStateEditView.as_view()
    ),

    # Workflow states actions

    url(
        regex=r'^workflows/states/(?P<workflow_state_id>\d+)/actions/$',
        name='workflow_state_action_list',
        view=WorkflowStateActionListView.as_view()
    ),
    url(
        regex=r'^workflows/states/(?P<workflow_state_id>\d+)/actions/selection/$',
        name='workflow_state_action_selection',
        view=WorkflowStateActionSelectionView.as_view(),
    ),
    url(
        regex=r'^workflows/states/(?P<workflow_state_id>\d+)/actions/(?P<class_path>[a-zA-Z0-9_.]+)/create/$',
        name='workflow_state_action_create',
        view=WorkflowStateActionCreateView.as_view()
    ),
    url(
        regex=r'^workflows/states/actions/(?P<workflow_state_action_id>\d+)/delete/$',
        view=WorkflowStateActionDeleteView.as_view(),
        name='workflow_state_action_delete'
    ),
    url(
        regex=r'^workflows/states/actions/(?P<workflow_state_action_id>\d+)/edit/$',
        name='workflow_state_action_edit',
        view=WorkflowStateActionEditView.as_view()
    ),

    # Workflow transitions

    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/transitions/$',
        name='workflow_transition_list',
        view=WorkflowTransitionListView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/transitions/create/$',
        name='workflow_transition_create',
        view=WorkflowTransitionCreateView.as_view()
    ),
    url(
        regex=r'^workflows/transitions/(?P<workflow_transition_id>\d+)/delete/$',
        name='workflow_transition_delete',
        view=WorkflowTransitionDeleteView.as_view()
    ),
    url(
        regex=r'^workflows/transitions/(?P<workflow_transition_id>\d+)/edit/$',
        name='workflow_transition_edit',
        view=WorkflowTransitionEditView.as_view()
    ),
    url(
        regex=r'^workflows/transitions/(?P<workflow_transition_id>\d+)/triggers/$',
        name='workflow_transition_triggers',
        view=WorkflowTransitionTriggerEventListView.as_view()
    ),

    # Workflow runtime proxies

    url(
        regex=r'^workflow_runtime_proxies/$', name='workflow_runtime_proxy_list',
        view=WorkflowRuntimeProxyListView.as_view()
    ),
    url(
        regex=r'^workflow_runtime_proxies/(?P<workflow_runtime_proxy_id>\d+)/documents/$',
        name='workflow_runtime_proxy_document_list',
        view=WorkflowRuntimeProxyDocumentListView.as_view()
    ),
    url(
        regex=r'^workflow_runtime_proxies/(?P<workflow_runtime_proxy_id>\d+)/states/$',
        name='workflow_runtime_proxy_state_list',
        view=WorkflowRuntimeProxyStateListView.as_view()
    ),
    url(
        regex=r'^workflow_runtime_proxies/states/(?P<workflow_runtime_proxy_state_id>\d+)/documents/$',
        name='workflow_runtime_proxy_state_document_list',
        view=WorkflowRuntimeProxyStateDocumentListView.as_view()
    ),

    # Workflow instances

    url(
        regex=r'^documents/(?P<document_id>\d+)/workflows/$',
        name='document_workflow_instance_list',
        view=DocumentWorkflowInstanceListView.as_view()
    ),
    url(
        regex=r'^documents/workflows/(?P<workflow_instance_id>\d+)/$',
        name='workflow_instance_detail',
        view=WorkflowInstanceDetailView.as_view()
    ),
    url(
        regex=r'^documents/workflows/(?P<workflow_instance_id>\d+)/transition/$',
        name='workflow_instance_transition',
        view=WorkflowInstanceTransitionView.as_view()
    ),

    # Workflow tools

    url(
        regex=r'^tools/workflows/all/launch/$',
        name='tool_launch_all_workflows',
        view=ToolLaunchAllWorkflows.as_view()
    )
]

api_router_entries = (
    {
        'prefix': r'workflows', 'viewset': WorkflowAPIViewSet,
        'basename': 'workflow'
    },
    {
        'prefix': r'workflows/(?P<workflow_id>[^/.]+)/states',
        'viewset': WorkflowStateAPIViewSet, 'basename': 'workflow-state'
    },
    {
        'prefix': r'workflows/(?P<workflow_id>[^/.]+)/transitions',
        'viewset': WorkflowTransitionAPIViewSet,
        'basename': 'workflow-transition'
    }
    #{
    #    'prefix': r'metadata_types/(?P<metadata_type_id>[^/.]+)/document_type_relations',
    #    'viewset': MetadataTypeDocumentTypeRelationAPIViewSet,
    #    'basename': 'metadata_type-document_type_relation'
    #},
)

'''
api_urls = [
    url(
        regex=r'^workflows/$', name='workflow-list',
        view=APIWorkflowListView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/$',
        name='workflow-detail', view=APIWorkflowView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/image/$',
        name='workflow-image', view=APIWorkflowImageView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/document_types/$',
        name='workflow-document-type-list',
        view=APIWorkflowDocumentTypeList.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/document_types/(?P<document_type_id>\d+)/$',
        name='workflow-document-type-detail',
        view=APIWorkflowDocumentTypeView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/states/$',
        name='workflowstate-list',
        view=APIWorkflowStateListView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/states/(?P<state_id>\d+)/$',
        name='workflowstate-detail', view=APIWorkflowStateView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/transitions/$',
        name='workflowtransition-list',
        view=APIWorkflowTransitionListView.as_view()
    ),
    url(
        regex=r'^workflows/(?P<workflow_id>\d+)/transitions/(?P<transition_id>\d+)/$',
        name='workflowtransition-detail',
        view=APIWorkflowTransitionView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/workflows/$',
        name='workflowinstance-list',
        view=APIWorkflowInstanceListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/workflows/(?P<workflow_id>\d+)/$',
        name='workflowinstance-detail',
        view=APIWorkflowInstanceView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/workflows/(?P<workflow_id>\d+)/log_entries/$',
        name='workflowinstancelogentry-list',
        view=APIWorkflowInstanceLogEntryListView.as_view()
    ),
    url(
        regex=r'^document_types/(?P<document_type_id>\d+)/workflows/$',
        name='documenttype-workflow-list',
        view=APIDocumentTypeWorkflowListView.as_view()
    )
]
'''

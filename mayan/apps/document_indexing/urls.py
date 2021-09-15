from __future__ import unicode_literals

from django.conf.urls import url

"""
from .api_views import (
    APIDocumentIndexTemplateListView, APIIndexTemplateListView,
    APIIndexNodeInstanceDocumentListView, APIIndexTemplateListView,
    APIIndexTemplateView, APIIndexView
)
"""
from .views import (
    DocumentIndexInstanceNodeListView, IndexInstanceNodeView, IndexInstancesRebuildView,
    IndexInstanceView, IndexTemplateCreateView, IndexTemplateDeleteView,
    IndexTemplateDocumentTypesView, IndexTemplateEditView,
    IndexTemplateListView, IndexTemplateNodeCreateView,
    IndexTemplateNodeDeleteView, IndexTemplateNodeEditView,
    IndexTemplateNodeListView
)

urlpatterns = [
    url(
        regex=r'^documents/(?P<document_id>\d+)/indexes/$',
        name='document_index_instance_list',
        view=DocumentIndexInstanceNodeListView.as_view()
    ),
    url(
        regex=r'^index_instances/$', name='index_instance_list',
        view=IndexInstanceView.as_view()
    ),
    url(
        regex=r'^index_instances/nodes/(?P<index_instance_node_id>\d+)/$',
        name='index_instance_node_view', view=IndexInstanceNodeView.as_view()
    ),
    url(
        regex=r'^index_instances/rebuild/$', name='index_instances_rebuild',
        view=IndexInstancesRebuildView.as_view()
    ),
    url(
        regex=r'^index_templates/$', name='index_template_list',
        view=IndexTemplateListView.as_view()
    ),
    url(
        regex=r'^index_templates/create/$', name='index_template_create',
        view=IndexTemplateCreateView.as_view()
    ),
    url(
        regex=r'^index_templates/(?P<index_template_id>\d+)/delete/$',
        name='index_template_delete', view=IndexTemplateDeleteView.as_view()
    ),
    url(
        regex=r'^index_templates/(?P<index_template_id>\d+)/document_types/$',
        name='index_template_document_types',
        view=IndexTemplateDocumentTypesView.as_view()
    ),
    url(
        regex=r'^index_templates/(?P<index_template_id>\d+)/edit/$',
        name='index_template_edit', view=IndexTemplateEditView.as_view()
    ),
    url(
        regex=r'^index_templates/(?P<index_template_id>\d+)/nodes/$',
        name='index_template_view', view=IndexTemplateNodeListView.as_view()
    ),
    url(
        regex=r'^index_templates/nodes/(?P<index_template_node_id>\d+)/create/$',
        name='index_template_node_create',
        view=IndexTemplateNodeCreateView.as_view()
    ),
    url(
        regex=r'^index_templates/nodes/(?P<index_template_node_id>\d+)/delete/$',
        name='index_template_node_delete',
        view=IndexTemplateNodeDeleteView.as_view()
    ),
    url(
        regex=r'^index_templates/nodes/(?P<index_template_node_id>\d+)/edit/$',
        name='index_template_node_edit',
        view=IndexTemplateNodeEditView.as_view()
    )
]

"""
api_urls = [
    url(
        regex=r'^index_templates/nodes/(?P<index_instance_node_pk>\d+)/documents/$',
        name='index-node-documents',
        view=APIIndexNodeInstanceDocumentListView.as_view(),
    ),
    url(
        regex=r'^index_templates/templates/(?P<index_template_node_pk>\d+)/$',
        name='index-template-detail', view=APIIndexTemplateView.as_view()
    ),
    url(
        regex=r'^index_templates/(?P<index_pk>\d+)/$', name='index-detail',
        view=APIIndexView.as_view()
    ),
    url(
        regex=r'^index_templates/(?P<index_pk>\d+)/templates/$',
        name='index-template-detail', view=APIIndexTemplateListView.as_view()
    ),
    url(
        regex=r'^index_templates/$', name='index-list',
        view=APIIndexTemplateListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/indexes/$',
        name='document-index-list',
        view=APIDocumentIndexTemplateListView.as_view()
    ),
]
"""

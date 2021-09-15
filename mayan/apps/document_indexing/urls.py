from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIDocumentIndexListView, APIIndexListView,
    APIIndexNodeInstanceDocumentListView, APIIndexTemplateListView,
    APIIndexTemplateView, APIIndexView
)
from .views import (
    DocumentIndexNodeListView, IndexInstanceNodeView, IndexListView,
    RebuildIndexesView, SetupIndexCreateView, SetupIndexDeleteView,
    SetupIndexDocumentTypesView, SetupIndexEditView, SetupIndexListView,
    SetupIndexTreeTemplateListView, TemplateNodeCreateView,
    TemplateNodeDeleteView, TemplateNodeEditView
)

urlpatterns = [
    url(
        regex=r'^indexes/$', name='index_setup_list',
        view=SetupIndexListView.as_view()
    ),
    url(
        regex=r'^indexes/create/$', name='index_setup_create',
        view=SetupIndexCreateView.as_view()
    ),
    url(
        regex=r'^indexes/(?P<index_pk>\d+)/delete/$',
        name='index_setup_delete', view=SetupIndexDeleteView.as_view()
    ),
    url(
        regex=r'^indexes/(?P<index_pk>\d+)/edit/$',
        name='index_setup_edit', view=SetupIndexEditView.as_view()
    ),
    url(
        regex=r'^indexes/(?P<index_pk>\d+)/templates/$',
        name='index_setup_view', view=SetupIndexTreeTemplateListView.as_view()
    ),
    url(
        regex=r'^indexes/(?P<index_pk>\d+)/document_types/$',
        name='index_setup_document_types',
        view=SetupIndexDocumentTypesView.as_view()
    ),
    url(
        regex=r'^indexes/templates/nodes/(?P<index_template_node_pk>\d+)/create/child/$',
        name='template_node_create', view=TemplateNodeCreateView.as_view()
    ),
    url(
        regex=r'^indexes/templates/nodes/(?P<index_template_node_pk>\d+)/edit/$',
        name='template_node_edit', view=TemplateNodeEditView.as_view()
    ),
    url(
        regex=r'^indexes/templates/nodes/(?P<index_template_node_pk>\d+)/delete/$',
        name='template_node_delete', view=TemplateNodeDeleteView.as_view()
    ),
    url(
        regex=r'^indexes/instances/list/$', name='index_list',
        view=IndexListView.as_view()
    ),
    url(
        regex=r'^indexes/instances/node/(?P<index_instance_node_pk>\d+)/$',
        name='index_instance_node_view', view=IndexInstanceNodeView.as_view()
    ),

    url(
        regex=r'^indexes/rebuild/$', name='rebuild_index_instances',
        view=RebuildIndexesView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/indexes/$',
        name='document_index_list', view=DocumentIndexNodeListView.as_view()
    ),
]

api_urls = [
    url(
        regex=r'^indexes/nodes/(?P<index_instance_node_pk>[0-9]+)/documents/$',
        name='index-node-documents',
        view=APIIndexNodeInstanceDocumentListView.as_view(),
    ),
    url(
        regex=r'^indexes/templates/(?P<index_template_node_pk>[0-9]+)/$',
        name='index-template-detail', view=APIIndexTemplateView.as_view()
    ),
    url(
        regex=r'^indexes/(?P<index_pk>\d+)/$', name='index-detail',
        view=APIIndexView.as_view()
    ),
    url(
        regex=r'^indexes/(?P<index_pk>\d+)/templates/$',
        name='index-template-detail', view=APIIndexTemplateListView.as_view()
    ),
    url(
        regex=r'^indexes/$', name='index-list',
        view=APIIndexListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/indexes/$',
        name='document-index-list',
        view=APIDocumentIndexListView.as_view()
    ),
]

from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    DocumentMetadataAPIViewSet, MetadataTypeAPIViewSet,
    MetadataTypeDocumentTypeRelationAPIViewSet
)
from .views import (
    DocumentMetadataAddView, DocumentMetadataEditView,
    DocumentMetadataListView, DocumentMetadataRemoveView,
    DocumentTypeMetadataTypes, MetadataTypeCreateView, MetadataTypeDeleteView,
    MetadataTypesDocumentTypes, MetadataTypeEditView, MetadataTypeListView
)

urlpatterns = [
    url(
        regex=r'^metadata_types/$', name='metadata_type_list',
        view=MetadataTypeListView.as_view()
    ),
    url(
        regex=r'^metadata_types/create/$', name='metadata_type_create',
        view=MetadataTypeCreateView.as_view()
    ),
    url(
        regex=r'^metadata_types/(?P<metadata_type_id>\d+)/delete/$',
        name='metadata_type_delete', view=MetadataTypeDeleteView.as_view()
    ),
    url(
        regex=r'^metadata_types/(?P<metadata_type_id>\d+)/edit/$',
        name='metadata_type_edit', view=MetadataTypeEditView.as_view()
    ),
    url(
        regex=r'^metadata_types/(?P<metadata_type_id>\d+)/document_types/$',
        name='metadata_type_document_types',
        view=MetadataTypesDocumentTypes.as_view()
    ),
    url(
        regex=r'^document_types/(?P<document_type_id>\d+)/metadata_types/$',
        name='document_type_metadata_types',
        view=DocumentTypeMetadataTypes.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/edit/$',
        name='document_metadata_edit', view=DocumentMetadataEditView.as_view()
    ),
    url(
        regex=r'^documents/multiple/edit/$',
        name='document_multiple_metadata_edit',
        view=DocumentMetadataEditView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/view/$',
        name='document_metadata_view',
        view=DocumentMetadataListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/add/$',
        name='document_metadata_add', view=DocumentMetadataAddView.as_view()
    ),
    url(
        regex=r'^documents/multiple/add/$',
        name='document_multiple_metadata_add',
        view=DocumentMetadataAddView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/remove/$',
        name='document_metadata_remove',
        view=DocumentMetadataRemoveView.as_view()
    ),
    url(
        regex=r'^documents/multiple/remove/$',
        name='document_multiple_metadata_remove',
        view=DocumentMetadataRemoveView.as_view()
    )
]

api_router_entries = (
    {
        'prefix': r'metadata_types', 'viewset': MetadataTypeAPIViewSet,
        'basename': 'metadata_type'
    },
    {
        'prefix': r'metadata_types/(?P<metadata_type_id>[^/.]+)/document_type_relations',
        'viewset': MetadataTypeDocumentTypeRelationAPIViewSet,
        'basename': 'metadata_type-document_type_relation'
    },
    {
        'prefix': r'documents/(?P<document_id>[^/.]+)/metadata',
        'viewset': DocumentMetadataAPIViewSet, 'basename': 'document-metadata'
    }
)

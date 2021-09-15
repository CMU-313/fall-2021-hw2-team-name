from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIDocumentMetadataListView, APIDocumentMetadataView,
    APIDocumentTypeMetadataTypeListView, APIDocumentTypeMetadataTypeView,
    APIMetadataTypeListView, APIMetadataTypeView
)
from .views import (
    DocumentMetadataAddView, DocumentMetadataEditView,
    DocumentMetadataListView, DocumentMetadataRemoveView,
    MetadataTypeCreateView, MetadataTypeDeleteView, MetadataTypeEditView,
    MetadataTypeListView, SetupDocumentTypeMetadataTypes,
    SetupMetadataTypesDocumentTypes
)

urlpatterns = [
    url(
        regex=r'^documents/(?P<pk>\d+)/edit/$', name='document_metadata_edit',
        view=DocumentMetadataEditView.as_view()
    ),
    url(
        regex=r'^documents/multiple/edit/$',
        name='document_multiple_metadata_edit',
        view=DocumentMetadataEditView.as_view()
    ),
    url(
        regex=r'^documents/(?P<pk>\d+)/view/$', name='document_metadata_view',
        view=DocumentMetadataListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<pk>\d+)/add/$', name='document_metadata_add',
        view=DocumentMetadataAddView.as_view()
    ),
    url(
        regex=r'^documents/multiple/add/$',
        name='document_multiple_metadata_add',
        view=DocumentMetadataAddView.as_view()
    ),
    url(
        regex=r'^documents/(?P<pk>\d+)/remove/$',
        name='document_metadata_remove',
        view=DocumentMetadataRemoveView.as_view()
    ),
    url(
        regex=r'^documents/multiple/remove/$',
        name='document_multiple_metadata_remove',
        view=DocumentMetadataRemoveView.as_view()
    ),

    url(
        regex=r'^types/list/$', name='metadata_type_list',
        view=MetadataTypeListView.as_view()
    ),
    url(
        regex=r'^types/create/$', name='metadata_type_create',
        view=MetadataTypeCreateView.as_view()
    ),
    url(
        regex=r'^types/(?P<pk>\d+)/edit/$', name='metadata_type_edit',
        view=MetadataTypeEditView.as_view()
    ),
    url(
        regex=r'^types/(?P<pk>\d+)/delete/$', name='metadata_type_delete',
        view=MetadataTypeDeleteView.as_view()
    ),
    url(
        regex=r'^document_types/(?P<pk>\d+)/metadata_types/$',
        name='document_type_metadata_types',
        view=SetupDocumentTypeMetadataTypes.as_view()
    ),
    url(
        regex=r'^metadata_types/(?P<pk>\d+)/document_types/$',
        name='metadata_type_document_types',
        view=SetupMetadataTypesDocumentTypes.as_view()
    ),
]

api_urls = [
    url(
        regex=r'^metadata_types/$', name='metadatatype-list',
        view=APIMetadataTypeListView.as_view()
    ),
    url(
        regex=r'^metadata_types/(?P<metadata_type_pk>\d+)/$',
        name='metadatatype-detail',
        view=APIMetadataTypeView.as_view()
    ),
    url(
        regex=r'^document_types/(?P<document_type_pk>\d+)/metadata_types/$',
        name='documenttypemetadatatype-list',
        view=APIDocumentTypeMetadataTypeListView.as_view()
    ),
    url(
        regex=r'^document_types/(?P<document_type_pk>\d+)/metadata_types/(?P<metadata_type_pk>\d+)/$',
        name='documenttypemetadatatype-detail',
        view=APIDocumentTypeMetadataTypeView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/metadata/$',
        name='documentmetadata-list',
        view=APIDocumentMetadataListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/metadata/(?P<metadata_pk>\d+)/$',
        name='documentmetadata-detail',
        view=APIDocumentMetadataView.as_view()
    ),
]

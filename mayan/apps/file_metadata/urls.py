from __future__ import unicode_literals

from django.conf.urls import url

from .views import (
    DocumentDriverListView, DocumentSubmitView, DocumentTypeSettingsEditView,
    DocumentTypeSubmitView, DocumentVersionDriverEntryFileMetadataListView
)

urlpatterns = [
    url(
        r'^documents/(?P<pk>\d+)/drivers/$', DocumentDriverListView.as_view(),
        name='document_driver_list'
    ),
    url(
        r'^documents/(?P<pk>\d+)/submit/$', DocumentSubmitView.as_view(),
        name='document_submit'
    ),
    url(
        r'^documents/multiple/submit/$', DocumentSubmitView.as_view(),
        name='document_multiple_submit'
    ),
    url(
        r'^document_types/(?P<pk>\d+)/ocr/settings/$',
        DocumentTypeSettingsEditView.as_view(),
        name='document_type_settings'
    ),
    url(
        r'^document_types/submit/$', DocumentTypeSubmitView.as_view(),
        name='document_type_submit'
    ),
    url(
        r'^document_version_driver/(?P<pk>\d+)/attributes/$',
        DocumentVersionDriverEntryFileMetadataListView.as_view(),
        name='document_version_driver_file_metadata_list'
    ),
]

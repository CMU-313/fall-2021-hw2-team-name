from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    DocumentPageOCRAPIViewSet, DocumentOCRAPIViewSet,
    DocumentVersionOCRAPIViewSet
)
from .views import (
    DocumentOCRContentView, DocumentOCRDownloadView,
    DocumentOCRErrorsListView, DocumentPageOCRContentView, DocumentSubmitView,
    DocumentTypeSettingsEditView, DocumentTypeSubmitView, EntryListView
)

urlpatterns = [
    url(
        regex=r'^document_types/ocr/submit/$', name='document_type_submit',
        view=DocumentTypeSubmitView.as_view()
    ),
    url(
        regex=r'^document_types/(?P<document_type_id>\d+)/ocr/settings/$',
        name='document_type_settings',
        view=DocumentTypeSettingsEditView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/ocr/content/$',
        name='document_content', view=DocumentOCRContentView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/ocr/download/$',
        name='document_download', view=DocumentOCRDownloadView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/ocr/errors/$',
        name='document_error_list',
        view=DocumentOCRErrorsListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/ocr/submit/$',
        name='document_submit', view=DocumentSubmitView.as_view()
    ),
    url(
        regex=r'^documents/multiple/ocr/submit/$',
        name='document_multiple_submit',
        view=DocumentSubmitView.as_view()
    ),
    url(
        regex=r'^documents/pages/(?P<document_page_id>\d+)/ocr/content/$',
        name='document_page_content',
        view=DocumentPageOCRContentView.as_view()
    ),
    url(
        regex=r'^errors/$', name='entry_list',
        view=EntryListView.as_view()
    )
]

api_router_entries = (
    {
        'prefix': r'documents',
        'viewset': DocumentOCRAPIViewSet, 'basename': 'document-ocr'
    },
    {
        'prefix': r'documents/(?P<document_id>\d+)/document_versions',
        'viewset': DocumentVersionOCRAPIViewSet, 'basename': 'document_version-ocr'
    },
    {
        'prefix': r'documents/(?P<document_id>\d+)/document_versions/(?P<document_version_id>\d+)/document_pages',
        'viewset': DocumentPageOCRAPIViewSet, 'basename': 'document_page-ocr'
    }
)

from __future__ import unicode_literals

from django.conf.urls import url

from .views import (
    AllDocumentSignatureVerifyView, DocumentVersionDetachedSignatureCreateView,
    DocumentVersionEmbeddedSignatureCreateView,
    DocumentVersionSignatureDeleteView, DocumentVersionSignatureDetailView,
    DocumentVersionSignatureDownloadView, DocumentVersionSignatureListView,
    DocumentVersionSignatureUploadView
)

urlpatterns = [
    url(
        regex=r'^signatures/(?P<signature_id>\d+)/$',
        name='document_version_signature_details',
        view=DocumentVersionSignatureDetailView.as_view()
    ),
    url(
        regex=r'^signatures/(?P<signature_id>\d+)/download/$',
        name='document_version_signature_download',
        view=DocumentVersionSignatureDownloadView.as_view()
    ),
    url(
        regex=r'^signatures/(?P<signature_id>\d+)/delete/$',
        name='document_version_signature_delete',
        view=DocumentVersionSignatureDeleteView.as_view()
    ),
    url(
        regex=r'^documents/versions/(?P<document_version_id>\d+)/signatures/$',
        name='document_version_signature_list',
        view=DocumentVersionSignatureListView.as_view()
    ),
    url(
        regex=r'^documents/versions/(?P<document_version_id>\d+)/signatures/detached/create/$',
        name='document_version_signature_detached_create',
        view=DocumentVersionDetachedSignatureCreateView.as_view()
    ),
    url(
        regex=r'^documents/versions/(?P<document_version_id>\d+)/signatures/detached/upload/$',
        name='document_version_signature_upload',
        view=DocumentVersionSignatureUploadView.as_view()
    ),
    url(
        regex=r'^documents/versions/(?P<document_version_id>\d+)/signatures/embedded/create/$',
        name='document_version_signature_embedded_create',
        view=DocumentVersionEmbeddedSignatureCreateView.as_view()
    ),
    url(
        regex=r'^tools/documents/versions/signatures/verify/$',
        name='all_document_version_signature_verify',
        view=AllDocumentSignatureVerifyView.as_view()
    )
]

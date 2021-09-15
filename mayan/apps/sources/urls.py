from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIStagingSourceFileImageView, APIStagingSourceFileView,
    APIStagingSourceListView, APIStagingSourceView
)
from .views import (
    SourceCheckView, SourceCreateView, SourceDeleteView,
    SourceEditView, SourceListView, SourceLogView,
    StagingFileDeleteView, UploadInteractiveVersionView, UploadInteractiveView
)
from .wizards import DocumentCreateWizard

urlpatterns = [
    url(
        regex=r'^sources/$', name='source_list',
        view=SourceListView.as_view()
    ),
    url(
        regex=r'^sources/(?P<source_type>\w+)/create/$',
        name='source_create', view=SourceCreateView.as_view()
    ),
    url(
        regex=r'^sources/(?P<source_id>\d+)/check/$', name='source_check',
        view=SourceCheckView.as_view()
    ),
    url(
        regex=r'^sources/(?P<source_id>\d+)/delete/$',
        name='source_delete', view=SourceDeleteView.as_view()
    ),
    url(
        regex=r'^sources/(?P<source_id>\d+)/edit/$', name='source_edit',
        view=SourceEditView.as_view()
    ),
    url(
        regex=r'^sources/(?P<source_id>\d+)/logs/$', name='source_logs',
        view=SourceLogView.as_view()
    ),

    url(
        regex=r'^sources/(?P<source_id>\d+)/document/upload/$',
        name='upload_interactive', view=UploadInteractiveView.as_view()
    ),
    url(
        regex=r'^sources/document/upload/$', name='upload_interactive',
        view=UploadInteractiveView.as_view()
    ),

    url(
        regex=r'^sources/(?P<source_id>\d+)/documents/(?P<document_id>\d+)/versions/upload/$',
        name='upload_version', view=UploadInteractiveVersionView.as_view()
    ),
    url(
        regex=r'^sources/documents/(?P<document_id>\d+)/version/upload/$',
        name='upload_version', view=UploadInteractiveVersionView.as_view()
    ),
    url(
        regex=r'^sources/wizard/$', name='document_create_multiple',
        view=DocumentCreateWizard.as_view()
    ),
    url(
        regex=r'^staging_files/(?P<staging_folder_id>\d+)/(?P<encoded_filename>.+)/delete/$',
        name='staging_file_delete', view=StagingFileDeleteView.as_view()
    ),
]

api_urls = [
    url(
        regex=r'^staging_folders/file/(?P<staging_folder_id>\d+)/(?P<encoded_filename>.+)/image/$',
        name='stagingfolderfile-image-view',
        view=APIStagingSourceFileImageView.as_view()
    ),
    url(
        regex=r'^staging_folders/file/(?P<staging_folder_id>\d+)/(?P<encoded_filename>.+)/$',
        name='stagingfolderfile-detail', view=APIStagingSourceFileView.as_view()
    ),
    url(
        regex=r'^staging_folders/$', name='stagingfolder-list',
        view=APIStagingSourceListView.as_view()
    ),
    url(
        regex=r'^staging_folders/(?P<staging_folder_id>\d+)/$',
        name='stagingfolder-detail', view=APIStagingSourceView.as_view()
    )
]

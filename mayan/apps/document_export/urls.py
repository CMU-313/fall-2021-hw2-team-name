from django.conf.urls import url

from .views import DocumentExportDownloadView

urlpatterns = [
    url(
        regex=r'^documents/(?P<document_id>\d+)/export/$',
        name='document_export', view=DocumentExportDownloadView.as_view()
    ),
]

from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APICabinetDocumentListView, APICabinetDocumentView, APICabinetListView,
    APICabinetView, APIDocumentCabinetListView
)
from .views import (
    CabinetChildAddView, CabinetCreateView, CabinetDeleteView,
    CabinetDetailView, CabinetEditView, CabinetListView,
    DocumentAddToCabinetView, DocumentCabinetListView,
    DocumentRemoveFromCabinetView
)

urlpatterns = [
    url(
        regex=r'^cabinets/$', name='cabinet_list',
        view=CabinetListView.as_view()
    ),
    url(
        regex=r'^cabinets/create/$', name='cabinet_create',
        view=CabinetCreateView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_pk>\d+)/$', name='cabinet_view',
        view=CabinetDetailView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_pk>\d+)/delete/$', name='cabinet_delete',
        view=CabinetDeleteView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_pk>\d+)/edit/$', name='cabinet_edit',
        view=CabinetEditView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_pk>\d+)/child/add/$',
        name='cabinet_child_add', view=CabinetChildAddView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/cabinets/add/$',
        name='document_cabinet_add', view=DocumentAddToCabinetView.as_view()
    ),
    url(
        regex=r'^documents/multiple/cabinets/add/$',
        name='document_multiple_cabinet_add',
        view=DocumentAddToCabinetView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/cabinets/remove/$',
        name='document_cabinet_remove',
        view=DocumentRemoveFromCabinetView.as_view()
    ),
    url(
        regex=r'^documents/multiple/cabinets/remove/$',
        name='document_multiple_cabinet_remove',
        view=DocumentRemoveFromCabinetView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/cabinets/list/$',
        name='document_cabinet_list', view=DocumentCabinetListView.as_view()
    ),
]

api_urls = [
    url(
        regex=r'^cabinets/(?P<cabinet_pk>\d+)/documents/(?P<document_pk>\d+)/$',
        name='cabinet-document', view=APICabinetDocumentView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_pk>\d+)/documents/$',
        name='cabinet-document-list', view=APICabinetDocumentListView.as_view()
    ),
    url(
        regex=r'^cabinets/(?P<cabinet_pk>\d+)/$', name='cabinet-detail',
        view=APICabinetView.as_view()
    ),
    url(
        regex=r'^cabinets/$', name='cabinet-list',
        view=APICabinetListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_pk>\d+)/cabinets/$',
        name='document-cabinet-list', view=APIDocumentCabinetListView.as_view()
    ),
]

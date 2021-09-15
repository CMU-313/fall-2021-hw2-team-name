from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIResolvedSmartLinkDocumentListView, APIResolvedSmartLinkListView,
    APIResolvedSmartLinkView, APISmartLinkConditionListView,
    APISmartLinkConditionView, APISmartLinkListView, APISmartLinkView
)
from .views import (
    DocumentSmartLinkListView, ResolvedSmartLinkView,
    SetupSmartLinkDocumentTypesView, SmartLinkConditionCreateView,
    SmartLinkConditionDeleteView, SmartLinkConditionEditView,
    SmartLinkConditionListView, SmartLinkCreateView, SmartLinkDeleteView,
    SmartLinkEditView, SmartLinkListView
)

urlpatterns = [
    url(
        regex=r'^smart_links/$', name='smart_link_list',
        view=SmartLinkListView.as_view()
    ),
    url(
        regex=r'^smart_links/create/$', name='smart_link_create',
        view=SmartLinkCreateView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>\d+)/delete/$',
        name='smart_link_delete', view=SmartLinkDeleteView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>\d+)/edit/$',
        name='smart_link_edit', view=SmartLinkEditView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>\d+)/document_types/$',
        name='smart_link_document_types',
        view=SetupSmartLinkDocumentTypesView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>\d+)/conditions/$',
        name='smart_link_condition_list',
        view=SmartLinkConditionListView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>\d+)/conditions/create/$',
        name='smart_link_condition_create',
        view=SmartLinkConditionCreateView.as_view()
    ),
    url(
        regex=r'^smart_links/conditions/(?P<smart_link_condition_id>\d+)/edit/$',
        name='smart_link_condition_edit',
        view=SmartLinkConditionEditView.as_view()
    ),
    url(
        regex=r'^smart_links/conditions/(?P<smart_link_condition_id>\d+)/delete/$',
        name='smart_link_condition_delete',
        view=SmartLinkConditionDeleteView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/resolved_smart_links/$',
        name='resolved_smart_links_for_document',
        view=DocumentSmartLinkListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/resolved_smart_links/(?P<smart_link_id>\d+)/$',
        name='resolved_smart_link_details', view=ResolvedSmartLinkView.as_view()
    )
]

api_urls = [
    url(
        regex=r'^smart_links/$', name='smartlink-list',
        view=APISmartLinkListView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>\d+)/$',
        name='smartlink-detail', view=APISmartLinkView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>\d+)/conditions/$',
        name='smartlinkcondition-list',
        view=APISmartLinkConditionListView.as_view()
    ),
    url(
        regex=r'^smart_links/(?P<smart_link_id>\d+)/conditions/(?P<condition_id>\d+)/$',
        name='smartlinkcondition-detail',
        view=APISmartLinkConditionView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/resolved_smart_links/$',
        name='resolvedsmartlink-list',
        view=APIResolvedSmartLinkListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/resolved_smart_links/(?P<smart_link_id>\d+)/$',
        name='resolvedsmartlink-detail',
        view=APIResolvedSmartLinkView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/resolved_smart_links/(?P<smart_link_id>\d+)/documents/$',
        name='resolvedsmartlinkdocument-list',
        view=APIResolvedSmartLinkDocumentListView.as_view()
    )
]

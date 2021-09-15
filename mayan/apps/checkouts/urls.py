from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import APICheckedoutDocumentListView, APICheckedoutDocumentView
from .views import (
    DocumentCheckinView, DocumentCheckoutView, DocumentCheckoutDetailView,
    DocumentCheckoutListView
)

urlpatterns = [
    url(
        regex=r'^documents/$', name='document_checkout_list',
        view=DocumentCheckoutListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/check_in/$',
        name='document_check_in', view=DocumentCheckinView.as_view()
    ),
    url(
        regex=r'^documents/multiple/check_in/$',
        name='document_multiple_check_in', view=DocumentCheckinView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/checkout/$',
        name='document_checkout', view=DocumentCheckoutView.as_view()
    ),
    url(
        regex=r'^documents/multiple/checkout/$',
        name='document_multiple_checkout', view=DocumentCheckoutView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/checkout/info/$',
        name='document_checkout_info', view=DocumentCheckoutDetailView.as_view()
    ),
]

api_urls = [
    url(
        regex=r'^checkouts/$', name='checkout-document-list',
        view=APICheckedoutDocumentListView.as_view()
    ),
    url(
        regex=r'^checkouts/(?P<document_id>\d+)/checkout_info/$',
        name='checkedout-document-view',
        view=APICheckedoutDocumentView.as_view()
    ),
]

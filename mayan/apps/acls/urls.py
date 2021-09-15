from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import ObjectACLAPIViewSet
from .views import (
    ACLCreateView, ACLDeleteView, ACLListView, ACLPermissionsView
)

urlpatterns = [
    url(
        regex=r'^objects/(?P<app_label>[-\w]+)/(?P<model_name>[-\w]+)/(?P<object_id>\d+)/create/$',
        name='acl_create', view=ACLCreateView.as_view()
    ),
    url(
        regex=r'^objects/(?P<app_label>[-\w]+)/(?P<model_name>[-\w]+)/(?P<object_id>\d+)/list/$',
        name='acl_list', view=ACLListView.as_view()
    ),
    url(
        regex=r'^acls/(?P<acl_id>\d+)/delete/$', name='acl_delete',
        view=ACLDeleteView.as_view()
    ),
    url(
        regex=r'^acls/(?P<acl_id>\d+)/permissions/$', name='acl_permissions',
        view=ACLPermissionsView.as_view()
    ),
]

api_router_entries = (
    {
        'prefix': r'apps/(?P<app_label>[^/.]+)/models/(?P<model_name>[^/.]+)/objects/(?P<object_id>[^/.]+)/acls',
        'viewset': ObjectACLAPIViewSet, 'basename': 'object-acl'
    },
)

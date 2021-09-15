from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    PermissionNamespaceAPIViewSet, PermissionAPIViewSet, RoleAPIViewSet
)
from .views import (
    GroupRolesView, RoleCreateView, RoleDeleteView, RoleEditView,
    RoleGroupsView, RoleListView, RolePermissionsView
)

urlpatterns = [
    url(
        regex=r'^groups/(?P<group_id>\d+)/roles/$', name='group_roles',
        view=GroupRolesView.as_view()
    ),
    url(
        regex=r'^roles/create/$', name='role_create',
        view=RoleCreateView.as_view()
    ),
    url(
        regex=r'^roles/(?P<role_id>\d+)/delete/$', name='role_delete',
        view=RoleDeleteView.as_view()
    ),
    url(
        regex=r'^roles/(?P<role_id>\d+)/edit/$', name='role_edit',
        view=RoleEditView.as_view()
    ),
    url(
        regex=r'^roles/(?P<role_id>\d+)/groups/$', name='role_groups',
        view=RoleGroupsView.as_view()
    ),
    url(
        regex=r'^roles/(?P<role_id>\d+)/permissions/$', name='role_permissions',
        view=RolePermissionsView.as_view()
    ),
    url(regex=r'^roles/list/$', name='role_list', view=RoleListView.as_view()),
]

api_router_entries = (
    {
        'prefix': r'permission_namespaces', 'viewset': PermissionNamespaceAPIViewSet,
        'basename': 'permission_namespace'
    },
    {
        'prefix': r'permission_namespaces/(?P<permission_namespace_name>[^/.]+)/permissions',
        'viewset': PermissionAPIViewSet, 'basename': 'permission'
    },
    {'prefix': r'roles', 'viewset': RoleAPIViewSet, 'basename': 'role'},
)

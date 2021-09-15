from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APICurrentUserView, APIGroupListView, APIGroupView, APIUserGroupList,
    APIUserListView, APIUserView
)
from .views import (
    CurrentUserDetailsView, CurrentUserEditView, GroupCreateView,
    GroupDeleteView, GroupEditView, GroupListView, GroupMembersView,
    UserCreateView, UserDeleteView, UserDetailsView, UserEditView,
    UserGroupsView, UserListView, UserOptionsEditView, UserSetPasswordView
)

urlpatterns = [
    url(r'^groups/list/$', GroupListView.as_view(), name='group_list'),
    url(r'^groups/create/$', GroupCreateView.as_view(), name='group_create'),
    url(
        r'^groups/(?P<pk>\d+)/edit/$', GroupEditView.as_view(),
        name='group_edit'
    ),
    url(
        r'^groups/(?P<pk>\d+)/delete/$', GroupDeleteView.as_view(),
        name='group_delete'
    ),
    url(
        r'^groups/(?P<pk>\d+)/members/$', GroupMembersView.as_view(),
        name='group_members'
    ),

    url(
        r'^users/current/$', CurrentUserDetailsView.as_view(),
        name='current_user_details'
    ),
    url(
        r'^users/current/edit/$', CurrentUserEditView.as_view(),
        name='current_user_edit'
    ),
    url(r'^users/list/$', UserListView.as_view(), name='user_list'),
    url(r'^users/create/$', UserCreateView.as_view(), name='user_create'),
    url(
        r'^users/(?P<pk>\d+)/delete/$', UserDeleteView.as_view(),
        name='user_delete'
    ),
    url(r'^users/(?P<pk>\d+)/edit/$', UserEditView.as_view(), name='user_edit'),
    url(
        r'^users/(?P<pk>\d+)/$', UserDetailsView.as_view(),
        name='user_details'
    ),
    url(
        r'^users/multiple/delete/$', UserDeleteView.as_view(),
        name='user_multiple_delete'
    ),
    url(
        r'^users/(?P<pk>\d+)/set_password/$', UserSetPasswordView.as_view(),
        name='user_set_password'
    ),
    url(
        r'^users/multiple/set_password/$', UserSetPasswordView.as_view(),
        name='user_multiple_set_password'
    ),
    url(
        r'^users/(?P<pk>\d+)/groups/$', UserGroupsView.as_view(),
        name='user_groups'
    ),
    url(
        r'^users/(?P<pk>\d+)/options/$',
        UserOptionsEditView.as_view(),
        name='user_options'
    ),
]

api_urls = [
    url(r'^groups/$', APIGroupListView.as_view(), name='group-list'),
    url(
        r'^groups/(?P<pk>[0-9]+)/$', APIGroupView.as_view(),
        name='group-detail'
    ),
    url(r'^users/$', APIUserListView.as_view(), name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/$', APIUserView.as_view(), name='user-detail'),
    url(
        r'^users/current/$', APICurrentUserView.as_view(), name='user-current'
    ),
    url(
        r'^users/(?P<pk>[0-9]+)/groups/$', APIUserGroupList.as_view(),
        name='users-group-list'
    ),
]

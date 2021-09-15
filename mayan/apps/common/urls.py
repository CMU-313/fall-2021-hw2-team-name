from __future__ import unicode_literals

from django.conf.urls import url
from django.views.i18n import javascript_catalog, set_language

from .api_views import ContentTypeAPIViewSet, TemplateAPIViewSet
from .views import (
    AboutView, CheckVersionView, CurrentUserLocaleProfileDetailsView,
    CurrentUserLocaleProfileEditView, FaviconRedirectView, HomeView,
    LicenseView, ObjectErrorLogEntryListClearView, ObjectErrorLogEntryListView,
    PackagesLicensesView, RootView, SetupListView, ToolsListView,
    multi_object_action_view
)

urlpatterns = [
    url(regex=r'^$', name='root', view=RootView.as_view()),
    url(regex=r'^home/$', name='home', view=HomeView.as_view()),
    url(regex=r'^about/$', name='about_view', view=AboutView.as_view()),
    url(
        regex=r'^check_version/$', name='check_version_view',
        view=CheckVersionView.as_view()
    ),
    url(regex=r'^license/$', name='license_view', view=LicenseView.as_view()),
    url(
        regex=r'^packages/licenses/$', name='packages_licenses_view',
        view=PackagesLicensesView.as_view()
    ),
    url(
        regex=r'^objects/multiple/action/$', name='multi_object_action_view',
        view=multi_object_action_view
    ),
    url(regex=r'^setup/$', name='setup_list', view=SetupListView.as_view()),
    url(regex=r'^tools/$', name='tools_list', view=ToolsListView.as_view()),
    url(
        regex=r'^users/current/locale/$',
        name='current_user_locale_profile_details',
        view=CurrentUserLocaleProfileDetailsView.as_view()
    ),
    url(
        regex=r'^users/current/locale/edit/$',
        name='current_user_locale_profile_edit',
        view=CurrentUserLocaleProfileEditView.as_view()
    ),
    url(
        regex=r'^objects/(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_id>\d+)/errors/$',
        name='object_error_list', view=ObjectErrorLogEntryListView.as_view()
    ),
    url(
        regex=r'^objects/(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_id>\d+)/errors/clear/$',
        name='object_error_list_clear',
        view=ObjectErrorLogEntryListClearView.as_view()
    ),
]

urlpatterns += [
    url(
        regex=r'^favicon\.ico$', view=FaviconRedirectView.as_view()
    ),
    url(
        regex=r'^jsi18n/(?P<packages>\S+?)/$', name='javascript_catalog',
        view=javascript_catalog
    ),
    url(
        regex=r'^set_language/$', name='set_language', view=set_language
    ),
]

api_router_entries = (
    {
        'prefix': r'content_types', 'viewset': ContentTypeAPIViewSet,
        'basename': 'content_type'
    },
    {
        'prefix': r'templates', 'viewset': TemplateAPIViewSet,
        'basename': 'template'
    },
)

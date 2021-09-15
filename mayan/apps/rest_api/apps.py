from __future__ import unicode_literals

from django.apps import apps
from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from rest_framework import routers

from mayan.apps.common import MayanAppConfig, menu_tools

from .links import (
    link_api, link_api_documentation, link_api_documentation_redoc
)
from .licenses import *  # NOQA


class RESTAPIApp(MayanAppConfig):
    app_url = 'api'
    app_namespace = 'rest_api'
    name = 'mayan.apps.rest_api'
    verbose_name = _('REST API')

    def ready(self):
        super(RESTAPIApp, self).ready()
        from .urls import urlpatterns

        settings.STRONGHOLD_PUBLIC_URLS += (r'^/%s/.+$' % self.app_url,)
        menu_tools.bind_links(
            links=(
                link_api, link_api_documentation, link_api_documentation_redoc
            )
        )
        router = routers.DefaultRouter()

        for app in apps.get_app_configs():
            if getattr(app, 'has_rest_api', False):
                try:
                    app_api_router_entries = import_string(
                        dotted_path='{}.urls.api_router_entries'.format(app.name)
                    )
                except ImportError:
                    pass
                else:
                    for entry in app_api_router_entries:
                        router.register(**entry)

                try:
                    app_api_urlpatterns = import_string(
                        dotted_path='{}.urls.api_urlpatterns'.format(app.name)
                    )
                except ImportError:
                    pass
                else:
                    urlpatterns.extend(app_api_urlpatterns)

        urlpatterns.extend(router.urls)

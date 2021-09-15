from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.common import (
    MayanAppConfig, menu_setup, menu_object, menu_secondary
)
from mayan.apps.navigation import SourceColumn

from .classes import Namespace, Setting
from .links import (
    link_namespace_detail, link_namespace_list, link_namespace_root_list,
    link_setting_edit
)
from .widgets import setting_widget


class SmartSettingsApp(MayanAppConfig):
    app_namespace = 'settings'
    app_url = 'settings'
    has_tests = True
    name = 'mayan.apps.smart_settings'
    verbose_name = _('Smart settings')

    def ready(self):
        super(SmartSettingsApp, self).ready()

        Namespace.initialize()

        SourceColumn(
            func=lambda context: len(context['object'].settings),
            label=_('Setting count'), source=Namespace
        )
        SourceColumn(
            func=lambda context: setting_widget(context['object']),
            label=_('Name'), source=Setting
        )
        SourceColumn(
            attribute='serialized_value', label=_('Value'), source=Setting
        )
        SourceColumn(
            func=lambda context: _('Yes') if context['object'].environment_variable else _('No'),
            label=_('Overrided by environment variable?'), source=Setting
        )

        menu_secondary.bind_links(
            links=(link_namespace_root_list,), sources=(
                Namespace, Setting, 'settings:namespace_list',
            )
        )
        menu_object.bind_links(
            links=(link_namespace_detail,), sources=(Namespace,)
        )
        menu_object.bind_links(
            links=(link_setting_edit,), sources=(Setting,)
        )
        menu_setup.bind_links(links=(link_namespace_list,))

        Setting.save_last_known_good()

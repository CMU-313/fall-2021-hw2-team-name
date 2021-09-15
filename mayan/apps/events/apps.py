from __future__ import unicode_literals

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common import (
    MayanAppConfig, menu_object, menu_secondary, menu_tools, menu_topbar,
    menu_user
)
from mayan.apps.common.widgets import ObjectLinkWidget, TwoStateWidget
from mayan.apps.navigation import SourceColumn

from .licenses import *  # NOQA
from .links import (
    link_current_user_events, link_event_types_subscriptions_list,
    link_events_list, link_notification_mark_read,
    link_notification_mark_read_all, link_user_notifications_list
)
from .widgets import (
    widget_event_actor_link, widget_event_type_link
)


class EventsApp(MayanAppConfig):
    app_namespace = 'events'
    app_url = 'events'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.events'
    verbose_name = _('Events')

    def ready(self):
        super(EventsApp, self).ready()
        Action = apps.get_model(app_label='actstream', model_name='Action')
        Notification = self.get_model(model_name='Notification')
        StoredEventType = self.get_model(model_name='StoredEventType')

        SourceColumn(
            attribute='timestamp', is_identifier=True,
            is_sortable=True, label=_('Date and time'), source=Action
        )
        SourceColumn(
            func=widget_event_actor_link, label=_('Actor'), source=Action
        )
        SourceColumn(
            func=widget_event_type_link, label=_('Event'), source=Action
        )
        SourceColumn(
            attribute='action_object', label=_('Action object'), source=Action,
            widget=ObjectLinkWidget
        )

        SourceColumn(
            attribute='target', label=_('Target'), source=Action,
            widget=ObjectLinkWidget
        )

        SourceColumn(
            source=StoredEventType, label=_('Namespace'), attribute='namespace'
        )
        SourceColumn(
            source=StoredEventType, label=_('Label'), attribute='label'
        )

        SourceColumn(
            attribute='action__timestamp', is_identifier=True,
            is_sortable=True, label=_('Date and time'), source=Notification
        )
        SourceColumn(
            func=widget_event_actor_link, kwargs={'attribute': 'action'},
            label=_('Actor'), source=Notification
        )
        SourceColumn(
            func=widget_event_type_link, kwargs={'attribute': 'action'},
            label=_('Event'), source=Notification
        )
        SourceColumn(
            attribute='action.target', label=_('Target'), source=Notification,
            widget=ObjectLinkWidget
        )

        SourceColumn(
            attribute='read', is_sortable=True, label=_('Seen'),
            source=Notification, widget=TwoStateWidget
        )

        menu_object.bind_links(
            links=(link_notification_mark_read,), sources=(Notification,)
        )
        menu_secondary.bind_links(
            links=(link_notification_mark_read_all,),
            sources=('events:user_notifications_list',)
        )
        menu_tools.bind_links(links=(link_events_list,))
        menu_topbar.bind_links(
            links=(link_user_notifications_list,), position=1
        )
        menu_user.bind_links(
            links=(
                link_event_types_subscriptions_list, link_current_user_events
            ), position=50
        )

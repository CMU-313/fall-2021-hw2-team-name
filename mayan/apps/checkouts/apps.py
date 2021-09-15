from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from kombu import Exchange, Queue

from django.apps import apps
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls import ModelPermission
from mayan.apps.common import (
    MayanAppConfig, menu_facet, menu_main, menu_multi_item, menu_secondary
)
from mayan.apps.dashboards.dashboards import dashboard_main
from mayan.apps.events import ModelEventType
from mayan.celery import app

from .dashboard_widgets import DashboardWidgetTotalCheckouts
from .events import (
    event_document_auto_check_in, event_document_check_in,
    event_document_check_out, event_document_forceful_check_in
)
from .handlers import handler_check_new_version_creation
from .hooks import hook_is_new_version_allowed
from .links import (
    link_document_check_in, link_document_checkout, link_document_checkout_info,
    link_document_checkout_list, link_document_multiple_check_in,
    link_document_multiple_checkout
)
from .literals import CHECK_EXPIRED_CHECK_OUTS_INTERVAL
from .methods import (
    method_check_in, method_get_checkout_info, method_get_checkout_state,
    method_is_checked_out
)
from .permissions import (
    permission_document_check_in, permission_document_check_in_override,
    permission_document_checkout, permission_document_checkout_detail_view
)
from .queues import *  # NOQA
# This import is required so that celerybeat can find the task
from .tasks import task_check_expired_check_outs  # NOQA


class CheckoutsApp(MayanAppConfig):
    app_namespace = 'checkouts'
    app_url = 'checkouts'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.checkouts'
    verbose_name = _('Checkouts')

    def ready(self):
        super(CheckoutsApp, self).ready()

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )
        DocumentVersion = apps.get_model(
            app_label='documents', model_name='DocumentVersion'
        )

        Document.add_to_class(name='check_in', value=method_check_in)
        Document.add_to_class(
            name='get_checkout_info', value=method_get_checkout_info
        )
        Document.add_to_class(
            name='get_checkout_state', value=method_get_checkout_state
        )
        Document.add_to_class(
            name='is_checked_out', value=method_is_checked_out
        )

        DocumentVersion.register_pre_save_hook(
            func=hook_is_new_version_allowed
        )

        ModelEventType.register(
            model=Document, event_types=(
                event_document_auto_check_in, event_document_check_in,
                event_document_check_out, event_document_forceful_check_in
            )
        )

        ModelPermission.register(
            model=Document, permissions=(
                permission_document_checkout,
                permission_document_check_in,
                permission_document_check_in_override,
                permission_document_checkout_detail_view
            )
        )

        app.conf.beat_schedule.update(
            {
                'task_check_expired_check_outs': {
                    'task': 'mayan.apps.checkouts.tasks.task_check_expired_check_outs',
                    'schedule': timedelta(
                        seconds=CHECK_EXPIRED_CHECK_OUTS_INTERVAL
                    ),
                },
            }
        )

        app.conf.task_queues.append(
            Queue(
                'checkouts_periodic', Exchange('checkouts_periodic'),
                routing_key='checkouts_periodic', delivery_mode=1
            ),
        )

        app.conf.task_routes.update(
            {
                'mayan.apps.checkouts.tasks.task_check_expired_check_outs': {
                    'queue': 'checkouts_periodic'
                },
            }
        )

        dashboard_main.add_widget(
            widget=DashboardWidgetTotalCheckouts, order=-1
        )

        menu_facet.bind_links(links=(link_document_checkout_info,), sources=(Document,))
        menu_main.bind_links(links=(link_document_checkout_list,), position=98)
        menu_multi_item.bind_links(
            links=(
                link_document_multiple_check_in, link_document_multiple_checkout
            ), sources=(Document,)
        )
        menu_secondary.bind_links(
            links=(link_document_checkout, link_document_check_in),
            sources=(
                'checkouts:document_checkout_info', 'checkouts:document_checkout',
                'checkouts:document_check_in'
            )
        )

        pre_save.connect(
            dispatch_uid='checkouts_handler_check_new_version_creation',
            receiver=handler_check_new_version_creation,
            sender=DocumentVersion
        )

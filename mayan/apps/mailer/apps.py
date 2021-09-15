from __future__ import unicode_literals

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from kombu import Exchange, Queue

from mayan.apps.acls import ModelPermission
from mayan.apps.acls.links import link_acl_list
from mayan.apps.acls.permissions import (
    permission_acl_edit, permission_acl_view
)
from mayan.apps.common import (
    MayanAppConfig, menu_list_facet, menu_multi_item, menu_object,
    menu_secondary, menu_setup, menu_tools
)
from mayan.apps.common.widgets import TwoStateWidget
from mayan.apps.navigation import SourceColumn
from mayan.celery import app

from .classes import MailerBackend
from .links import (
    link_document_send, link_document_send_link, link_document_multiple_send,
    link_document_multiple_send_link, link_system_mailer_error_log,
    link_user_mailer_create, link_user_mailer_delete, link_user_mailer_edit,
    link_user_mailer_list, link_user_mailer_log_list, link_user_mailer_setup,
    link_user_mailer_test
)
from .permissions import (
    permission_mailing_link, permission_mailing_send_document,
    permission_user_mailer_delete, permission_user_mailer_edit,
    permission_user_mailer_use, permission_user_mailer_view
)
from .queues import *  # NOQA


class MailerApp(MayanAppConfig):
    app_namespace = 'mailer'
    app_url = 'mailer'
    has_tests = True
    name = 'mayan.apps.mailer'
    verbose_name = _('Mailer')

    def ready(self):
        super(MailerApp, self).ready()

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )

        LogEntry = self.get_model('LogEntry')
        UserMailer = self.get_model('UserMailer')

        MailerBackend.initialize()

        SourceColumn(attribute='datetime', source=LogEntry)
        SourceColumn(attribute='message', source=LogEntry)
        SourceColumn(attribute='label', is_identifier=True, source=UserMailer)
        SourceColumn(
            attribute='default', source=UserMailer, widget=TwoStateWidget
        )
        SourceColumn(
            attribute='enabled', source=UserMailer, widget=TwoStateWidget
        )
        SourceColumn(attribute='backend_label', source=UserMailer)

        ModelPermission.register(
            model=Document, permissions=(
                permission_mailing_link, permission_mailing_send_document
            )
        )

        ModelPermission.register(
            model=UserMailer, permissions=(
                permission_acl_edit, permission_acl_view,
                permission_user_mailer_delete, permission_user_mailer_edit,
                permission_user_mailer_view, permission_user_mailer_use
            )
        )

        app.conf.task_queues.append(
            Queue('mailing', Exchange('mailing'), routing_key='mailing'),
        )

        app.conf.task_routes.update(
            {
                'mayan.apps.mailer.tasks.task_send_document': {
                    'queue': 'mailing'
                },
            }
        )

        menu_list_facet.bind_links(
            links=(
                link_acl_list, link_user_mailer_log_list,
            ), sources=(UserMailer,)
        )

        menu_multi_item.bind_links(
            links=(
                link_document_multiple_send, link_document_multiple_send_link
            ), sources=(Document,)
        )

        menu_object.bind_links(
            links=(
                link_document_send_link, link_document_send
            ), sources=(Document,)
        )

        menu_object.bind_links(
            links=(
                link_user_mailer_edit, link_user_mailer_test,
                link_user_mailer_delete,
            ), sources=(UserMailer,)
        )

        menu_secondary.bind_links(
            links=(
                link_user_mailer_create, link_user_mailer_list,
            ), sources=(
                UserMailer, 'mailer:user_mailer_list',
                'mailer:user_mailer_backend_selection',
                'mailer:user_mailer_create',
            )
        )

        menu_tools.bind_links(links=(link_system_mailer_error_log,))

        menu_setup.bind_links(links=(link_user_mailer_setup,))

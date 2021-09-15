from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation import Link

from .icons import (
    icon_document_multiple_send, icon_document_multiple_send_link,
    icon_document_send, icon_document_send_link, icon_system_mailer_error_log,
    icon_user_mailer_create, icon_user_mailer_delete, icon_user_mailer_edit,
    icon_user_mailer_list, icon_user_mailer_setup, icon_user_mailer_test
)
from .permissions import (
    permission_mailing_link, permission_mailing_send_document,
    permission_user_mailer_create, permission_user_mailer_delete,
    permission_user_mailer_edit, permission_user_mailer_use,
    permission_user_mailer_view, permission_view_error_log
)

link_document_send = Link(
    icon_class=icon_document_send, kwargs={'document_id': 'resolved_object.pk'},
    permission=permission_mailing_send_document, text=_('Email document'),
    view='mailer:document_send'
)
link_document_send_link = Link(
    icon_class=icon_document_send_link,
    kwargs={'document_id': 'resolved_object.pk'},
    permission=permission_mailing_link, text=_('Email link'),
    view='mailer:document_send_link'
)
link_document_multiple_send = Link(
    icon_class=icon_document_multiple_send, text=_('Email document'),
    view='mailer:document_multiple_send'
)
link_document_multiple_send_link = Link(
    icon_class=icon_document_multiple_send_link, text=_('Email link'),
    view='mailer:document_multiple_send_link'
)
link_system_mailer_error_log = Link(
    icon_class=icon_system_mailer_error_log,
    permission=permission_view_error_log,
    text=_('System mailer error log'), view='mailer:system_mailer_error_log'
)
link_user_mailer_create = Link(
    icon_class=icon_user_mailer_create,
    permission=permission_user_mailer_create, text=_('User mailer create'),
    view='mailer:user_mailer_backend_selection'
)
link_user_mailer_delete = Link(
    icon_class=icon_user_mailer_delete,
    kwargs={'mailer_id': 'resolved_object.pk'},
    permission=permission_user_mailer_delete, tags='dangerous',
    text=_('Delete'), view='mailer:user_mailer_delete'
)
link_user_mailer_edit = Link(
    icon_class=icon_user_mailer_edit, kwargs={'mailer_id': 'object.pk'},
    permission=permission_user_mailer_edit, text=_('Edit'),
    view='mailer:user_mailer_edit'
)
link_user_mailer_log_list = Link(
    permission=permission_user_mailer_view, kwargs={'mailer_id': 'object.pk'},
    text=_('Log'), view='mailer:user_mailer_log'
)
link_user_mailer_list = Link(
    icon_class=icon_user_mailer_list,
    permission=permission_user_mailer_view,
    text=_('Mailing profiles list'), view='mailer:user_mailer_list'
)
link_user_mailer_setup = Link(
    icon_class=icon_user_mailer_setup,
    permission=permission_user_mailer_view,
    text=_('Mailing profiles'), view='mailer:user_mailer_list'
)
link_user_mailer_test = Link(
    icon_class=icon_user_mailer_test, kwargs={'mailer_id': 'object.pk'},
    permission=permission_user_mailer_use, text=_('Test'),
    view='mailer:user_mailer_test'
)

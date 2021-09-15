from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation import Link

from .icons import (
    icon_checkin_document, icon_checkout_document, icon_checkout_info
)
from .permissions import (
    permission_document_check_in, permission_document_checkout,
    permission_document_checkout_detail_view
)


def is_checked_out(context):
    try:
        return context['object'].is_checked_out()
    except KeyError:
        # Might not have permissions
        return False


def is_not_checked_out(context):
    try:
        return not context['object'].is_checked_out()
    except KeyError:
        # Might not have permissions
        return True


link_document_checkout_list = Link(
    icon_class=icon_checkout_info, text=_('Checkouts'),
    view='checkouts:document_checkout_list'
)
link_document_checkout = Link(
    condition=is_not_checked_out, icon_class=icon_checkout_document,
    kwargs={'document_id': 'object.pk'},
    permission=permission_document_checkout, text=_('Check out document'),
    view='checkouts:document_checkout',
)
link_document_multiple_checkout = Link(
    icon_class=icon_checkout_document,
    permission=permission_document_checkout, text=_('Check out'),
    view='checkouts:document_multiple_checkout',
)
link_document_check_in = Link(
    condition=is_checked_out, icon_class=icon_checkin_document,
    kwargs={'document_id': 'object.pk'}, permission=permission_document_check_in,
    text=_('Check in document'), view='checkouts:document_check_in',
)
link_document_multiple_check_in = Link(
    icon_class=icon_checkin_document, permission=permission_document_check_in,
    text=_('Check in'), view='checkouts:document_multiple_check_in',
)
link_document_checkout_info = Link(
    icon_class=icon_checkout_info, kwargs={'document_id': 'resolved_object.pk'},
    permission=permission_document_checkout_detail_view,
    text=_('Check in/out'), view='checkouts:document_checkout_info',
)

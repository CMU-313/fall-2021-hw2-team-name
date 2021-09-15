from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation import Link, Separator, Text

from .icons import (
    icon_current_user_details, icon_current_user_edit, icon_group,
    icon_group_create, icon_group_delete, icon_group_edit, icon_group_list,
    icon_group_members, icon_group_setup, icon_user_create, icon_user_delete,
    icon_user_edit, icon_user_list, icon_user_multiple_delete,
    icon_user_multiple_set_password, icon_user_set_options,
    icon_user_set_password, icon_user_setup
)
from .permissions import (
    permission_group_create, permission_group_delete, permission_group_edit,
    permission_group_view, permission_user_create, permission_user_delete,
    permission_user_edit, permission_user_view
)
from .utils import get_user_label_text


def condition_is_not_superuser(context):
    user = context['object']
    return not user.is_superuser and not user.is_staff


link_current_user_details = Link(
    icon_class=icon_current_user_details, text=_('User details'),
    view='user_management:current_user_details'
)
link_current_user_edit = Link(
    icon_class=icon_current_user_edit, text=_('Edit details'),
    view='user_management:current_user_edit'
)
link_group_create = Link(
    icon_class=icon_group_create, permission=permission_group_create,
    text=_('Create new group'), view='user_management:group_create'
)
link_group_delete = Link(
    icon_class=icon_group_delete, kwargs={'group_id': 'object.pk'},
    permission=permission_group_delete, tags='dangerous',
    text=_('Delete'), view='user_management:group_delete'
)
link_group_edit = Link(
    icon_class=icon_group_edit, kwargs={'group_id': 'object.pk'},
    permission=permission_group_edit, text=_('Edit'),
    view='user_management:group_edit'
)
link_group_list = Link(
    icon_class=icon_group_list, permission=permission_group_view,
    text=_('Groups'), view='user_management:group_list'
)
link_group_members = Link(
    icon_class=icon_group_members, kwargs={'group_id': 'object.pk'},
    permission=permission_group_edit, text=_('Users'),
    view='user_management:group_members'
)
link_group_setup = Link(
    icon_class=icon_group_setup, permission=permission_group_view,
    text=_('Groups'), view='user_management:group_list'
)
link_user_create = Link(
    icon_class=icon_user_create, permission=permission_user_create,
    text=_('Create new user'), view='user_management:user_create'
)
link_user_delete = Link(
    icon_class=icon_user_delete, kwargs={'user_id': 'object.pk'},
    permission=permission_user_delete, tags='dangerous', text=_('Delete'),
    view='user_management:user_delete'
)
link_user_edit = Link(
    icon_class=icon_user_edit, kwargs={'user_id': 'object.pk'},
    permission=permission_user_edit, text=_('Edit'),
    view='user_management:user_edit'
)
link_user_groups = Link(
    condition=condition_is_not_superuser, icon_class=icon_group,
    kwargs={'user_id': 'object.pk'}, permission=permission_user_edit,
    text=_('Groups'), view='user_management:user_groups'
)
link_user_list = Link(
    icon_class=icon_user_list, permission=permission_user_view,
    text=_('Users'), view='user_management:user_list'
)
link_user_multiple_delete = Link(
    icon_class=icon_user_multiple_delete,
    permission=permission_user_delete, tags='dangerous', text=_('Delete'),
    view='user_management:user_multiple_delete'
)
link_user_multiple_set_password = Link(
    icon_class=icon_user_multiple_set_password,
    permission=permission_user_edit, text=_('Set password'),
    view='user_management:user_multiple_set_password'
)
link_user_set_options = Link(
    icon_class=icon_user_set_options, kwargs={'user_id': 'object.pk'},
    permission=permission_user_edit, text=_('User options'),
    view='user_management:user_options'
)
link_user_set_password = Link(
    icon_class=icon_user_set_password, kwargs={'user_id': 'object.pk'},
    permission=permission_user_edit, text=_('Set password'),
    view='user_management:user_set_password'
)
link_user_setup = Link(
    icon_class=icon_user_setup, permission=permission_user_view,
    text=_('Users'), view='user_management:user_list'
)

separator_user_label = Separator()
text_user_label = Text(text=get_user_label_text)

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.icons import icon_document_type
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.navigation import Link

from .icons import (
    icon_smart_link_condition, icon_smart_link_condition_create,
    icon_smart_link_create, icon_smart_link_instances_for_document,
    icon_smart_link_setup
)
from .permissions import (
    permission_smart_link_create, permission_smart_link_delete,
    permission_smart_link_edit, permission_smart_link_view
)

link_smart_link_condition_create = Link(
    icon_class=icon_smart_link_condition_create,
    kwargs={'smart_link_id': 'object.pk'},
    permission=permission_smart_link_edit, text=_('Create condition'),
    view='linking:smart_link_condition_create'
)
link_smart_link_condition_delete = Link(
    kwargs={'smart_link_condition_id': 'resolved_object.pk'},
    permission=permission_smart_link_edit, tags='dangerous',
    text=_('Delete'), view='linking:smart_link_condition_delete'
)
link_smart_link_condition_edit = Link(
    kwargs={'smart_link_condition_id': 'resolved_object.pk'},
    permission=permission_smart_link_edit, text=_('Edit'),
    view='linking:smart_link_condition_edit'
)
link_smart_link_condition_list = Link(
    icon_class=icon_smart_link_condition, kwargs={'smart_link_id': 'object.pk'},
    permission=permission_smart_link_edit, text=_('Conditions'),
    view='linking:smart_link_condition_list'
)
link_smart_link_create = Link(
    icon_class=icon_smart_link_create, permission=permission_smart_link_create,
    text=_('Create new smart link'), view='linking:smart_link_create'
)
link_smart_link_delete = Link(
    kwargs={'smart_link_id': 'object.pk'},
    permission=permission_smart_link_delete, tags='dangerous',
    text=_('Delete'), view='linking:smart_link_delete'
)
link_smart_link_document_types = Link(
    icon_class=icon_document_type, kwargs={'document_type_id': 'object.pk'},
    permission=permission_smart_link_edit, text=_('Document types'),
    view='linking:smart_link_document_types'
)
link_smart_link_edit = Link(
    kwargs={'smart_link_id': 'object.pk'},
    permission=permission_smart_link_edit, text=_('Edit'),
    view='linking:smart_link_edit'
)
link_smart_link_instance_view = Link(
    kwargs={'document_id': 'document.pk', 'smart_link_id': 'object.pk'},
    permission=permission_smart_link_view, text=_('Documents'),
    view='linking:resolved_smart_link_details'
)
link_smart_link_instances_for_document = Link(
    icon_class=icon_smart_link_instances_for_document,
    kwargs={'document_id': 'resolved_object.pk'},
    permission=permission_document_view, text=_('Smart links'),
    view='linking:resolved_smart_links_for_document'
)
link_smart_link_list = Link(
    permission=permission_smart_link_view, text=_('Smart links'),
    view='linking:smart_link_list'
)
link_smart_link_setup = Link(
    icon_class=icon_smart_link_setup, permission=permission_smart_link_view,
    text=_('Smart links'), view='linking:smart_link_list'
)

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.icons import icon_document_type
from mayan.apps.navigation import Link, get_cascade_condition

from .icons import (
    icon_document_index_instance_list, icon_index, icon_index_template_create,
    icon_index_template_delete, icon_index_template_edit,
    icon_index_template_list, icon_index_template_node_create,
    icon_index_template_node_delete, icon_index_template_node_edit,
    icon_index_template_view, icon_index_instances_rebuild
)
from .permissions import (
    permission_document_indexing_create, permission_document_indexing_delete,
    permission_document_indexing_edit,
    permission_document_indexing_instance_view,
    permission_document_indexing_rebuild, permission_document_indexing_view
)


def condition_is_not_root_node(context):
    return not context['resolved_object'].is_root_node()


link_document_index_instance_list = Link(
    icon_class=icon_document_index_instance_list,
    kwargs={'document_id': 'resolved_object.pk'}, text=_('Indexes'),
    view='indexing:document_index_instance_list',
)
link_index_instances_rebuild = Link(
    condition=get_cascade_condition(
        app_label='document_indexing', model_name='Index',
        object_permission=permission_document_indexing_rebuild,
    ), icon_class=icon_index_instances_rebuild,
    description=_(
        'Deletes and creates from scratch all the document indexes.'
    ), text=_('Rebuild indexes'), view='indexing:index_instances_rebuild'
)
link_index_main_menu = Link(
    condition=get_cascade_condition(
        app_label='document_indexing', model_name='Index',
        object_permission=permission_document_indexing_instance_view,
    ), icon_class=icon_index, text=_('Indexes'),
    view='indexing:index_instance_list'
)
link_index_setup = Link(
    condition=get_cascade_condition(
        app_label='document_indexing', model_name='Index',
        object_permission=permission_document_indexing_view,
        view_permission=permission_document_indexing_create,
    ), icon_class=icon_index, text=_('Indexes'),
    view='indexing:index_template_list'
)
link_index_template_list = Link(
    icon_class=icon_index_template_list,
    text=_('Indexes'), view='indexing:index_template_list'
)
link_index_template_create = Link(
    icon_class=icon_index_template_create,
    permission=permission_document_indexing_create, text=_('Create index'),
    view='indexing:index_template_create'
)
link_index_template_delete = Link(
    icon_class=icon_index_template_delete,
    kwargs={'index_template_id': 'resolved_object.pk'},
    permission=permission_document_indexing_delete, tags='dangerous',
    text=_('Delete'), view='indexing:index_template_delete'
)
link_index_template_edit = Link(
    icon_class=icon_index_template_edit,
    kwargs={'index_template_id': 'resolved_object.pk'},
    permission=permission_document_indexing_edit, text=_('Edit'),
    view='indexing:index_template_edit'
)
link_index_template_view = Link(
    kwargs={'index_template_id': 'resolved_object.pk'}, icon_class=icon_index_template_view,
    permission=permission_document_indexing_edit, text=_('Tree template'),
    view='indexing:index_template_view'
)
link_index_template_document_types = Link(
    kwargs={'index_template_id': 'resolved_object.pk'}, icon_class=icon_document_type,
    permission=permission_document_indexing_edit, text=_('Document types'),
    view='indexing:index_template_document_types'
)
link_index_template_node_create = Link(
    icon_class=icon_index_template_node_create,
    kwargs={'index_template_node_id': 'resolved_object.pk'},
    text=_('New node'), view='indexing:index_template_node_create'
)
link_index_template_node_delete = Link(
    condition=condition_is_not_root_node,
    icon_class=icon_index_template_node_delete,
    kwargs={'index_template_node_id': 'resolved_object.pk'}, tags='dangerous',
    text=_('Delete'), view='indexing:index_template_node_delete'
)
link_index_template_node_edit = Link(
    condition=condition_is_not_root_node,
    icon_class=icon_index_template_node_edit,
    kwargs={'index_template_node_id': 'resolved_object.pk'}, text=_('Edit'),
    view='indexing:index_template_node_edit'
)

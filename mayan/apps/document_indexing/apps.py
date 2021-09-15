from __future__ import absolute_import, unicode_literals

from django.apps import apps
from django.db.models.signals import post_delete, post_save, pre_delete
from django.utils.translation import ugettext_lazy as _

from kombu import Exchange, Queue

from mayan.apps.acls import ModelPermission
from mayan.apps.acls.links import link_acl_list
from mayan.apps.acls.permissions import (
    permission_acl_edit, permission_acl_view
)
from mayan.apps.common import (
    MayanAppConfig, menu_facet, menu_list_facet, menu_main, menu_object,
    menu_secondary, menu_setup, menu_tools
)
from mayan.apps.common.widgets import TwoStateWidget
from mayan.apps.documents.signals import (
    post_document_created, post_initial_document_type
)
from mayan.apps.navigation import SourceColumn
from mayan.celery import app

from .handlers import (
    handler_create_default_document_index, handler_delete_empty,
    handler_index_document, handler_post_save_index_document,
    handler_remove_document
)
from .licenses import *  # NOQA
from .links import (
    link_document_index_list, link_index_main_menu, link_index_setup,
    link_index_setup_create, link_index_setup_delete,
    link_index_setup_document_types, link_index_setup_edit,
    link_index_setup_list, link_index_setup_view, link_rebuild_index_instances,
    link_template_node_create, link_template_node_delete,
    link_template_node_edit
)
from .permissions import (
    permission_document_indexing_create, permission_document_indexing_delete,
    permission_document_indexing_edit,
    permission_document_indexing_instance_view,
    permission_document_indexing_rebuild, permission_document_indexing_view
)
from .queues import *  # NOQA
from .widgets import get_instance_link, index_instance_item_link, node_level


class DocumentIndexingApp(MayanAppConfig):
    app_namespace = 'indexing'
    app_url = 'indexing'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.document_indexing'
    verbose_name = _('Document indexing')

    def ready(self):
        super(DocumentIndexingApp, self).ready()

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )

        DocumentType = apps.get_model(
            app_label='documents', model_name='DocumentType'
        )

        DocumentIndexInstanceNode = self.get_model(
            model_name='DocumentIndexInstanceNode'
        )

        Index = self.get_model(model_name='Index')
        IndexInstance = self.get_model(model_name='IndexInstance')
        IndexInstanceNode = self.get_model(model_name='IndexInstanceNode')
        IndexTemplateNode = self.get_model(model_name='IndexTemplateNode')

        ModelPermission.register(
            model=Index, permissions=(
                permission_acl_edit, permission_acl_view,
                permission_document_indexing_create,
                permission_document_indexing_delete,
                permission_document_indexing_edit,
                permission_document_indexing_instance_view,
                permission_document_indexing_rebuild,
                permission_document_indexing_view,
            )
        )

        SourceColumn(attribute='label', is_identifier=True, source=Index)
        SourceColumn(attribute='slug', source=Index)
        SourceColumn(
            attribute='enabled', source=Index, widget=TwoStateWidget
        )

        SourceColumn(
            func=lambda context: context[
                'object'
            ].instance_root.get_descendants_count(), label=_('Total levels'),
            source=IndexInstance,
        )
        SourceColumn(
            func=lambda context: context[
                'object'
            ].instance_root.get_descendants_document_count(
                user=context['request'].user
            ), label=_('Total documents'), source=IndexInstance
        )

        SourceColumn(
            func=lambda context: node_level(context['object']),
            label=_('Level'), source=IndexTemplateNode
        )
        SourceColumn(
            attribute='enabled', source=IndexTemplateNode,
            widget=TwoStateWidget
        )
        SourceColumn(
            attribute='link_documents', source=IndexTemplateNode,
            widget=TwoStateWidget
        )

        SourceColumn(
            func=lambda context: index_instance_item_link(context['object']),
            label=_('Level'), source=IndexInstanceNode
        )
        SourceColumn(
            func=lambda context: context['object'].get_descendants_count(),
            label=_('Levels'), source=IndexInstanceNode
        )
        SourceColumn(
            func=lambda context: context[
                'object'
            ].get_descendants_document_count(
                user=context['request'].user
            ), label=_('Documents'), source=IndexInstanceNode
        )

        SourceColumn(
            func=lambda context: get_instance_link(
                index_instance_node=context['object'],
            ), label=_('Level'), source=DocumentIndexInstanceNode
        )
        SourceColumn(
            func=lambda context: context['object'].get_descendants_count(),
            label=_('Levels'), source=DocumentIndexInstanceNode
        )
        SourceColumn(
            func=lambda context: context[
                'object'
            ].get_descendants_document_count(
                user=context['request'].user
            ), label=_('Documents'), source=DocumentIndexInstanceNode
        )

        app.conf.task_queues.append(
            Queue('indexing', Exchange('indexing'), routing_key='indexing'),
        )

        app.conf.task_routes.update(
            {
                'mayan.apps.document_indexing.tasks.task_delete_empty': {
                    'queue': 'indexing'
                },
                'mayan.apps.document_indexing.tasks.task_remove_document': {
                    'queue': 'indexing'
                },
                'mayan.apps.document_indexing.tasks.task_index_document': {
                    'queue': 'indexing'
                },
                'mayan.apps.document_indexing.tasks.task_rebuild_index': {
                    'queue': 'tools'
                },
            }
        )

        menu_facet.bind_links(
            links=(link_document_index_list,), sources=(Document,)
        )
        menu_list_facet.bind_links(
            links=(
                link_acl_list, link_index_setup_document_types,
                link_index_setup_view,
            ), sources=(Index,)
        )
        menu_object.bind_links(
            links=(
                link_index_setup_edit, link_index_setup_delete
            ), sources=(Index,)
        )
        menu_object.bind_links(
            links=(
                link_template_node_create, link_template_node_edit,
                link_template_node_delete
            ), sources=(IndexTemplateNode,)
        )
        menu_main.bind_links(links=(link_index_main_menu,), position=98)
        menu_secondary.bind_links(
            links=(link_index_setup_list, link_index_setup_create),
            sources=(
                Index, 'indexing:index_setup_list',
                'indexing:index_setup_create'
            )
        )
        menu_setup.bind_links(links=(link_index_setup,))
        menu_tools.bind_links(links=(link_rebuild_index_instances,))

        post_delete.connect(
            dispatch_uid='document_indexing_handler_delete_empty',
            receiver=handler_delete_empty,
            sender=Document
        )
        post_document_created.connect(
            dispatch_uid='document_indexing_handler_index_document',
            receiver=handler_index_document,
            sender=Document
        )
        post_initial_document_type.connect(
            dispatch_uid='document_indexing_handler_create_default_document_index',
            receiver=handler_create_default_document_index,
            sender=DocumentType
        )
        post_save.connect(
            dispatch_uid='document_indexing_handler_post_save_index_document',
            receiver=handler_post_save_index_document,
            sender=Document
        )
        pre_delete.connect(
            dispatch_uid='document_indexing_handler_remove_document',
            receiver=handler_remove_document,
            sender=Document
        )

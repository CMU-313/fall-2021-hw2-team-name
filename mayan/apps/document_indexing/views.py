from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.template import RequestContext
from django.urls import reverse, reverse_lazy
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.generics import (
    AssignRemoveView, FormView, SingleObjectCreateView, SingleObjectDeleteView,
    SingleObjectEditView, SingleObjectListView
)
from mayan.apps.common.mixins import ExternalObjectMixin
from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.documents.permissions import permission_document_type_view
from mayan.apps.documents.views import DocumentListView

from .forms import IndexTemplateFilteredForm, IndexTemplateNodeForm
from .html_widgets import node_tree
from .icons import icon_index
from .links import link_index_template_create
from .models import (
    DocumentIndexInstanceNode, Index, IndexInstance, IndexInstanceNode,
    IndexTemplateNode
)
from .permissions import (
    permission_document_indexing_create, permission_document_indexing_delete,
    permission_document_indexing_edit,
    permission_document_indexing_instance_view,
    permission_document_indexing_view
)
from .tasks import task_rebuild_index


class DocumentIndexInstanceNodeListView(ExternalObjectMixin, SingleObjectListView):
    """
    Show a list of indexes where the current document can be found
    """
    external_object_class = Document
    external_object_permission = permission_document_indexing_instance_view
    external_object_pk_url_kwarg = 'document_id'
    object_permission = permission_document_indexing_instance_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_index,
            'no_results_text': _(
                'Assign the document type of this document '
                'to an index to have it appear in instances of '
                'those indexes organization units. '
            ),
            'no_results_title': _(
                'This document is not in any index instance'
            ),
            'object': self.external_object,
            'title': _(
                'Index instance nodes containing document: %s'
            ) % self.external_object,
        }

    def get_source_queryset(self):
        return DocumentIndexInstanceNode.objects.get_for(
            document=self.external_object
        )


class IndexInstanceView(SingleObjectListView):
    object_permission = permission_document_indexing_instance_view

    def get_extra_context(self):
        return {
            'hide_links': True,
            'no_results_icon': icon_index,
            'no_results_main_link': link_index_template_create.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'This could mean that no index templates have been '
                'created or that there index templates '
                'but they are no properly defined.'
            ),
            'no_results_title': _('There are no index instances available.'),
            'title': _('Indexes'),
        }

    def get_source_queryset(self):
        queryset = IndexInstance.objects.filter(enabled=True)
        return queryset.filter(
            node_templates__index_instance_nodes__isnull=False
        ).distinct()


class IndexInstanceNodeView(ExternalObjectMixin, DocumentListView):
    external_object_class = IndexInstanceNode
    external_object_permission = permission_document_indexing_instance_view
    external_object_pk_url_kwarg = 'index_instance_node_id'
    template_name = 'document_indexing/node_details.html'

    def get_extra_context(self):
        context = super(IndexInstanceNodeView, self).get_extra_context()
        if not self.external_object.index_template_node.link_documents:
            context.pop('table_cell_container_classes', None)

        context.update(
            {
                'column_class': 'col-xs-12 col-sm-6 col-md-4 col-lg-3',
                'object': self.external_object,
                'navigation': mark_safe(
                    _('Navigation: %s') % node_tree(
                        node=self.external_object, user=self.request.user
                    )
                ),
                'title': _(
                    'Contents for index instance: %s'
                ) % self.external_object.get_full_path(),
            }
        )

        if not self.external_object.index_template_node.link_documents:
            context.update(
                {
                    'hide_object': True,
                    'list_as_items': False,
                }
            )

        return context

    def get_source_queryset(self):
        if self.external_object.index_template_node.link_documents:
            return self.external_object.documents.all()
        else:
            return self.external_object.get_children().order_by(
                'value'
            )


class IndexInstancesRebuildView(FormView):
    extra_context = {
        'title': _('Rebuild index instances'),
    }
    form_class = IndexTemplateFilteredForm

    def form_valid(self, form):
        count = 0
        for index_template in form.cleaned_data['index_templates']:
            task_rebuild_index.apply_async(
                kwargs=dict(index_template_id=index_template.pk)
            )
            count += 1

        messages.success(
            request=self.request, message=ungettext(
                singular='%(count)d index template queued for rebuild.',
                plural='%(count)d indexes templates queued for rebuild.',
                number=count
            ) % {
                'count': count,
            }
        )

        return super(IndexInstancesRebuildView, self).form_valid(form=form)

    def get_form_extra_kwargs(self):
        return {
            'user': self.request.user
        }

    def get_post_action_redirect(self):
        return reverse(viewname='common:tools_list')


class IndexTemplateCreateView(SingleObjectCreateView):
    extra_context = {'title': _('Create index')}
    fields = ('label', 'slug', 'enabled')
    model = Index
    post_action_redirect = reverse_lazy(viewname='indexing:index_template_list')
    view_permission = permission_document_indexing_create


class IndexTemplateDeleteView(SingleObjectDeleteView):
    model = Index
    object_permission = permission_document_indexing_delete
    pk_url_kwarg = 'index_template_id'
    post_action_redirect = reverse_lazy(viewname='indexing:index_template_list')

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Delete the index template: %s?') % self.object,
        }


class IndexTemplateDocumentTypesView(ExternalObjectMixin, AssignRemoveView):
    decode_content_type = True
    external_object_class = Index
    external_object_permission = permission_document_indexing_edit
    external_object_pk_url_kwarg = 'index_template_id'
    left_list_title = _('Available document types')
    object_permission = permission_document_indexing_edit
    right_list_title = _('Document types linked')

    def add(self, item):
        self.external_object.document_types.add(item)

    def get_document_type_queryset(self):
        return AccessControlList.objects.restrict_queryset(
            permission=permission_document_type_view,
            queryset=DocumentType.objects.all(), user=self.request.user
        )

    def get_extra_context(self):
        return {
            'object': self.external_object,
            'subtitle': _(
                'Only the documents of the types selected will be shown '
                'in the index when built. Only the events of the documents '
                'of the types select will trigger updates in the index.'
            ),
            'title': _(
                'Document types linked to index template: %s'
            ) % self.external_object
        }

    def left_list(self):
        return AssignRemoveView.generate_choices(
            self.get_document_type_queryset().exclude(
                id__in=self.external_object.document_types.all()
            )
        )

    def remove(self, item):
        self.external_object.document_types.remove(item)

    def right_list(self):
        return AssignRemoveView.generate_choices(
            choices=self.get_document_type_queryset() & self.external_object.document_types.all()
        )


class IndexTemplateEditView(SingleObjectEditView):
    fields = ('label', 'slug', 'enabled')
    model = Index
    object_permission = permission_document_indexing_edit
    pk_url_kwarg = 'index_template_id'
    post_action_redirect = reverse_lazy(viewname='indexing:index_template_list')

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Edit index template: %s') % self.object,
        }


class IndexTemplateListView(SingleObjectListView):
    model = Index
    object_permission = permission_document_indexing_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_index,
            'no_results_main_link': link_index_template_create.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'Indexes group document automatically into levels. Indexe are '
                'defined using template whose markers are replaced with '
                'direct properties of documents like label or description, or '
                'that of extended properties like metadata.'
            ),
            'no_results_title': _('There are no index templates.'),
            'title': _('Index templates'),
        }


class IndexTemplateNodeCreateView(ExternalObjectMixin, SingleObjectCreateView):
    external_object_class = IndexTemplateNode
    external_object_permission = permission_document_indexing_edit
    external_object_pk_url_kwarg = 'index_template_node_id'
    form_class = IndexTemplateNodeForm
    model = IndexTemplateNode

    def get_extra_context(self):
        return {
            'index': self.external_object.index,
            'navigation_object_list': ('index',),
            'title': _('Create child node of: %s') % self.external_object,
        }

    def get_initial(self):
        return {
            'index': self.external_object.index, 'parent': self.external_object
        }


class IndexTemplateNodeDeleteView(SingleObjectDeleteView):
    model = IndexTemplateNode
    object_permission = permission_document_indexing_edit
    pk_url_kwarg = 'index_template_node_id'

    def get_extra_context(self):
        return {
            'index': self.object.index,
            'navigation_object_list': ('index', 'node'),
            'node': self.object,
            'title': _(
                'Delete the index template node: %s?'
            ) % self.object,
        }

    def get_post_action_redirect(self):
        return reverse(
            viewname='indexing:index_template_view',
            kwargs={'index_template_id': self.object.index.pk}
        )


class IndexTemplateNodeEditView(SingleObjectEditView):
    form_class = IndexTemplateNodeForm
    model = IndexTemplateNode
    object_permission = permission_document_indexing_edit
    pk_url_kwarg = 'index_template_node_id'

    def get_extra_context(self):
        return {
            'index': self.object.index,
            'navigation_object_list': ('index', 'node'),
            'node': self.object,
            'title': _(
                'Edit the index template node: %s?'
            ) % self.object,
        }

    def get_post_action_redirect(self):
        return reverse(
            viewname='indexing:index_template_view',
            kwargs={'index_template_id': self.object.index.pk}
        )


class IndexTemplateNodeListView(ExternalObjectMixin, SingleObjectListView):
    external_object_class = Index
    external_object_permission = permission_document_indexing_edit
    external_object_pk_url_kwarg = 'index_template_id'

    def get_extra_context(self):
        return {
            'hide_object': True,
            'index': self.external_object,
            'navigation_object_list': ('index',),
            'title': _('Nodes for index template: %s') % self.external_object,
        }

    def get_source_queryset(self):
        return self.external_object.template_root.get_descendants(
            include_self=True
        )

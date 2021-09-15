from __future__ import absolute_import, unicode_literals

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls import ModelPermission
from mayan.apps.common import (
    MayanAppConfig, menu_facet, menu_object, menu_secondary
)
from mayan.apps.documents.search import document_page_search, document_search
from mayan.apps.events import ModelEventType
from mayan.apps.navigation import SourceColumn

from .events import (
    event_document_comment_created, event_document_comment_deleted
)
from .links import (
    link_comment_add, link_comment_delete, link_comments_for_document
)
from .permissions import (
    permission_comment_create, permission_comment_delete,
    permission_comment_view
)


class DocumentCommentsApp(MayanAppConfig):
    app_namespace = 'comments'
    app_url = 'comments'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.document_comments'
    verbose_name = _('Document comments')

    def ready(self):
        from actstream import registry
        super(DocumentCommentsApp, self).ready()

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )

        Comment = self.get_model('Comment')

        ModelEventType.register(
            model=Document, event_types=(
                event_document_comment_created, event_document_comment_deleted
            )
        )

        ModelPermission.register(
            model=Document, permissions=(
                permission_comment_create, permission_comment_delete,
                permission_comment_view
            )
        )

        ModelPermission.register_inheritance(
            model=Comment, related='document',
        )

        SourceColumn(source=Comment, label=_('Date'), attribute='submit_date')
        SourceColumn(
            func=lambda context: context['object'].user.get_full_name() if context['object'].user.get_full_name() else context['object'].user,
            label=_('User'), source=Comment
        )
        SourceColumn(source=Comment, label=_('Comment'), attribute='comment')

        document_page_search.add_model_field(
            label=_('Comments'),
            field='document_version__document__comments__comment',
        )
        document_search.add_model_field(
            label=_('Comments'),
            field='comments__comment'
        )

        menu_secondary.bind_links(
            links=(link_comment_add,),
            sources=(
                'comments:comments_for_document', 'comments:comment_add',
                'comments:comment_delete', 'comments:comment_multiple_delete'
            )
        )
        menu_object.bind_links(
            links=(link_comment_delete,), sources=(Comment,)
        )
        menu_facet.bind_links(
            links=(link_comments_for_document,), sources=(Document,)
        )

        registry.register(Comment)

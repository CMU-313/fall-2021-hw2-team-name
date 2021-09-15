from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation import Link

from .icons import (
    icon_comment_add, icon_comment_delete, icon_comments_for_document
)
from .permissions import (
    permission_comment_create, permission_comment_delete,
    permission_comment_view
)

link_comment_add = Link(
    icon_class=icon_comment_add, kwargs={'document_id': 'object.pk'},
    permission=permission_comment_create, text=_('Add comment'),
    view='comments:comment_add',
)
link_comment_delete = Link(
    icon_class=icon_comment_delete, kwargs={'comment_id': 'object.pk'},
    permission=permission_comment_delete, tags='dangerous',
    text=_('Delete'), view='comments:comment_delete',
)
link_comments_for_document = Link(
    icon_class=icon_comments_for_document,
    kwargs={'document_id': 'resolved_object.pk'},
    permission=permission_comment_view, text=_('Comments'),
    view='comments:comments_for_document',
)

from __future__ import unicode_literals

from django.template.loader import render_to_string
from django.utils.html import escape, mark_safe

from .icons import (
    icon_index, icon_index_level_up,
    icon_index_instance_node_with_documents
)


class IndexInstanceNodeWidget(object):
    def render(self, name, value):
        return render_to_string(
            template_name='document_indexing/index_instance_node.html',
            context={
                'index_instance_node': value,
            }
        )


class IndexTemplateNodeIndentationWidget(object):
    def render(self, name, value):
        return render_to_string(
            template_name='document_indexing/index_template_node_indentation.html',
            context={
                'index_template_node': value,
                'index_template_node_level': range(value.get_level()),
            }
        )


def get_instance_link(index_instance_node):
    """
    Return an HTML anchor to an index node instance
    """
    return mark_safe(
        s='<a href="{url}">{text}</a>'.format(
            url=index_instance_node.get_absolute_url(),
            text=escape(index_instance_node.get_full_path())
        )
    )


def node_tree(node, user):
    #TODO: Replace with a file template
    result = []

    result.append('<div class="list-group">')

    for ancestor in node.get_ancestors(include_self=True):
        if ancestor.is_root_node():
            element = node.index()
            icon = icon_index
        else:
            element = ancestor
            if element.index_template_node.link_documents:
                icon = icon_index_instance_node_with_documents
            else:
                icon = icon_index_level_up

        result.append(
            '<a href="{url}" class="list-group-item {active}"><span class="badge">{count}</span>{icon} {text}</a>'.format(
                url=element.get_absolute_url(),
                active='active' if element == node or node.get_ancestors(include_self=True).count() == 1 else '',
                count=element.get_item_count(user=user),
                icon=icon.render(),
                text=escape(element)
            )
        )

    result.append('</div>')

    return mark_safe(s=''.join(result))

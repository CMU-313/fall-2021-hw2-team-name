from __future__ import absolute_import, unicode_literals

from django.template.loader import render_to_string


class DocumentTagsWidget(object):
    """
    A tag widget that displays the tags for the given document
    """
    def render(self, name, value):
        return render_to_string(
            template_name='tags/document_tags_widget.html',
            context={
                'tags': value,
            }
        )


class TagWidget(object):
    def render(self, name, value):
        return render_to_string(
            template_name='tags/tag_widget.html',
            context={
                'tag': value,
            }
        )

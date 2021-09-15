from __future__ import unicode_literals

from ..models import Tag

from .literals import (
    TEST_TAG_COLOR, TEST_TAG_COLOR_EDITED, TEST_TAG_LABEL,
    TEST_TAG_LABEL_EDITED
)


class TagTestMixin(object):
    def _create_tag(self):
        self.tag = Tag.objects.create(
            color=TEST_TAG_COLOR, label=TEST_TAG_LABEL
        )

    def _request_tag_create_view(self):
        return self.post(
            viewname='tags:tag_create', data={
                'label': TEST_TAG_LABEL,
                'color': TEST_TAG_COLOR
            }
        )

    def _request_tag_delete_view(self):
        return self.post(
            viewname='tags:tag_delete', args=(self.tag.pk,)
        )

    def _request_tag_edit_view(self):
        return self.post(
            viewname='tags:tag_edit', args=(self.tag.pk,), data={
                'label': TEST_TAG_LABEL_EDITED, 'color': TEST_TAG_COLOR_EDITED
            }
        )

    def _request_multiple_delete_view(self):
        return self.post(
            viewname='tags:tag_multiple_delete',
            data={'id_list': self.tag.pk},
        )

    def _request_edit_tag_view(self):
        return self.post(
            viewname='tags:tag_edit', args=(self.tag.pk,), data={
                'label': TEST_TAG_LABEL_EDITED, 'color': TEST_TAG_COLOR_EDITED
            }
        )

    def _request_create_tag_view(self):
        return self.post(
            viewname='tags:tag_create', data={
                'label': TEST_TAG_LABEL,
                'color': TEST_TAG_COLOR
            }
        )

    def _request_attach_tag_view(self):
        return self.post(
            viewname='tags:tag_attach', args=(self.document.pk,), data={
                'tags': self.tag.pk,
                'user': self.user.pk
            }
        )

    def _request_multiple_attach_tag_view(self):
        return self.post(
            viewname='tags:multiple_documents_tag_attach', data={
                'id_list': self.document.pk, 'tags': self.tag.pk,
                'user': self.user.pk
            }
        )

    def _request_single_document_multiple_tag_remove_view(self):
        return self.post(
            viewname='tags:single_document_multiple_tag_remove',
            args=(self.document.pk,), data={
                'id_list': self.document.pk,
                'tags': self.tag.pk,
            }
        )

    def _request_multiple_documents_selection_tag_remove_view(self):
        return self.post(
            viewname='tags:multiple_documents_selection_tag_remove',
            data={
                'id_list': self.document.pk,
                'tags': self.tag.pk,
            }
        )

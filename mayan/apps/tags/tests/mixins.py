from __future__ import unicode_literals

from ..models import Tag

from .literals import (
    TEST_TAG_COLOR, TEST_TAG_COLOR_EDITED, TEST_TAG_LABEL, TEST_TAG_LABEL_2
    TEST_TAG_LABEL_EDITED
)


class TagTestMixin(object):
    def _create_test_tag(self):
        self.test_tag = Tag.objects.create(
            color=TEST_TAG_COLOR, label=TEST_TAG_LABEL
        )

    def _create_test_tag_2(self):
        self.test_tag_2 = Tag.objects.create(
            color=TEST_TAG_COLOR, label=TEST_TAG_LABEL_2
        )


class TagAPITestMixin(object):
    def _request_api_tag_create_view(self):
        return self.post(
            viewname='rest_api:tag-list', data={
                'color': TEST_TAG_COLOR, 'label': TEST_TAG_LABEL
            }
        )

    def _request_api_tag_create_and_attach_view(self):
        return self.post(
            viewname='rest_api:tag-list', data={
                'color': TEST_TAG_COLOR, 'label': TEST_TAG_LABEL,
                'document_id_list': self.document.pk
            }
        )

    def _request_api_tag_delete_view(self):
        return self.delete(
            viewname='rest_api:tag-detail', kwargs={'tag_id': self.test_tag.pk}
        )

    def _request_api_tag_edit_patch_view(self):
        return self.patch(
            viewname='rest_api:tag-detail', kwargs={
                'tag_id': self.test_tag.pk
            }, data={
                'label': TEST_TAG_LABEL_EDITED,
                'color': TEST_TAG_COLOR_EDITED
            }
        )

    def _request_api_tag_edit_put_view(self):
        return self.put(
            viewname='rest_api:tag-detail', kwargs={
                'tag_id': self.test_tag.pk
            }, data={
                'label': TEST_TAG_LABEL_EDITED,
                'color': TEST_TAG_COLOR_EDITED
            }
        )

    def _request_api_tag_list_view(self):
        return self.get(viewname='rest_api:tag-list')


class TagViewTestMixin(object):
    def _request_document_tag_multiple_attach_view(self):
        return self.post(
            viewname='tags:document_tag_multiple_attach',
            kwargs={'document_id': self.document.pk}, data={
                'tags': self.test_tag.pk,
            }
        )

    def _request_document_multiple_tag_multiple_attach_view(self):
        return self.post(
            viewname='tags:document_multiple_tag_multiple_attach', data={
                'id_list': self.document.pk, 'tags': self.test_tag.pk,
            }
        )

    def _request_document_tag_multiple_remove_view(self):
        return self.post(
            viewname='tags:document_tag_multiple_remove',
            kwargs={'document_id': self.document.pk}, data={
                'tags': self.test_tag.pk,
            }
        )

    def _request_document_multiple_tag_multiple_remove_view(self):
        return self.post(
            viewname='tags:document_multiple_tag_multiple_remove',
            data={
                'id_list': self.document.pk,
                'tags': self.test_tag.pk,
            }
        )

    def _request_document_tag_list_view(self):
        return self.get(
            viewname='tags:document_tag_list',
            kwargs={
                'document_id': self.document.pk,
            }
        )

    # Normal tag view

    def _request_tag_create_view(self):
        return self.post(
            viewname='tags:tag_create', data={
                'label': TEST_TAG_LABEL,
                'color': TEST_TAG_COLOR
            }
        )

    def _request_tag_delete_view(self):
        return self.post(
            viewname='tags:tag_delete', kwargs={'tag_id': self.test_tag.pk},
        )

    def _request_tag_edit_view(self):
        return self.post(
            viewname='tags:tag_edit', kwargs={'tag_id': self.test_tag.pk},
            data={
                'label': TEST_TAG_LABEL_EDITED, 'color': TEST_TAG_COLOR_EDITED
            }
        )

    def _request_tag_multiple_delete_view(self):
        return self.post(
            viewname='tags:tag_multiple_delete',
            data={'id_list': self.test_tag.pk}
        )

from __future__ import unicode_literals

from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_create
from mayan.apps.documents.tests import (
    GenericDocumentViewTestCase, TEST_SMALL_DOCUMENT_PATH,
)
from mayan.apps.sources.models import WebFormSource
from mayan.apps.sources.tests.literals import (
    TEST_SOURCE_LABEL, TEST_SOURCE_UNCOMPRESS_N
)


from .mixins import TagTestMixin


class TaggedDocumentUploadTestCase(TagTestMixin, GenericDocumentViewTestCase):
    auto_upload_document = False

    def setUp(self):
        super(TaggedDocumentUploadTestCase, self).setUp()
        self.source = WebFormSource.objects.create(
            enabled=True, label=TEST_SOURCE_LABEL,
            uncompress=TEST_SOURCE_UNCOMPRESS_N
        )

    def _request_upload_interactive_document_create_view(self):
        with open(TEST_SMALL_DOCUMENT_PATH, mode='rb') as file_object:
            return self.post(
                viewname='sources:upload_interactive',
                kwargs={'source_id': self.source.pk},
                data={
                    'document_type_id': self.document_type.pk,
                    'source-file': file_object,
                    'tags': ','.join(map(str, Tag.objects.values_list('pk', flat=True)))
                }
            )

    def test_upload_interactive_view_with_access(self):
        self._create_tag()

        self.grant_access(
            permission=permission_document_create, obj=self.document_type
        )
        response = self._request_upload_interactive_document_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertTrue(self.tag in Document.objects.first().tags.all())

    def test_upload_interactive_multiple_tags_view_with_access(self):
        self._create_tag()
        self._create_tag_2()

        self.grant_access(
            permission=permission_document_create, obj=self.document_type
        )
        response = self._request_upload_interactive_document_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertTrue(self.test_tag in Document.objects.first().tags.all())
        self.assertTrue(self.test_tag_2 in Document.objects.first().tags.all())

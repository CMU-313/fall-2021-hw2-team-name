from __future__ import unicode_literals

from django.test import override_settings

from mayan.apps.documents.tests import (
    TEST_HYBRID_DOCUMENT, GenericDocumentTestCase
)

from .literals import TEST_DOCUMENT_CONTENT


class DocumentAutoParsingTestCase(GenericDocumentTestCase):
    test_document_filename = TEST_HYBRID_DOCUMENT
    auto_create_document_type = False

    def test_disable_auto_parsing(self):
        self._create_document_type()
        self.document = self.upload_document()

        self.assertTrue(
            TEST_DOCUMENT_CONTENT not in self.document.get_content()
        )

    @override_settings(DOCUMENT_PARSING_AUTO_PARSING=True)
    def test_enabled_auto_parsing(self):
        self._create_document_type()
        self.document = self.upload_document()
        self.assertTrue(
            TEST_DOCUMENT_CONTENT in self.document.get_content()
        )

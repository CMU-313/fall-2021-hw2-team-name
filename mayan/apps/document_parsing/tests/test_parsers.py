from __future__ import unicode_literals

from mayan.apps.common.tests import BaseTestCase
from mayan.apps.documents.tests import TEST_HYBRID_DOCUMENT, DocumentTestMixin

from ..parsers import PopplerParser

from .literals import TEST_DOCUMENT_CONTENT


class ParserTestCase(DocumentTestMixin, BaseTestCase):
    test_document_filename = TEST_HYBRID_DOCUMENT

    def test_poppler_parser(self):
        parser = PopplerParser()

        parser.process_document_version(self.document.latest_version)

        self.assertTrue(
            TEST_DOCUMENT_CONTENT in self.document.pages.first().content.content
        )

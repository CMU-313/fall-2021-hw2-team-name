from __future__ import unicode_literals

from mayan.apps.documents.tests import GenericDocumentTestCase

from .mixins import SmartLinkTestMixin


class SmartLinkTestCase(SmartLinkTestMixin, GenericDocumentTestCase):
    def test_dynamic_label(self):
        self._create_test_smart_link()

        self.test_smart_link.document_types.add(self.document_type)

        self.assertEqual(
            self.test_smart_link.get_dynamic_label(document=self.document),
            self.document.label
        )

from django.core.exceptions import ValidationError

from mayan.apps.tests.tests.base import BaseTestCase
from mayan.apps.documents.tests.mixins import DocumentTestMixin

from .mixins import CabinetTestMixin


class CabinetCopyTestCase(
    CabinetTestMixin, DocumentTestMixin, BaseTestCase
):
    def setUp(self):
        super().setUp()
        self._create_test_cabinet()
        self._create_test_cabinet_child

    def test_cabinet_copy(self):
        self.test_cabinet.documents.add(self.test_document)

        instance_copy = self.test_cabinet.copy_instance()
        source_queryset = self.test_cabinet.get_family().values(
            'parent_id', 'label', 'documents'
        )
        copy_queryset = instance_copy.get_family().values(
            'parent_id', 'label', 'documents'
        )

        self.assertEqual(list(source_queryset), list(copy_queryset))

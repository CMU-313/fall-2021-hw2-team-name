from __future__ import unicode_literals

import os
import random
import string
import time

from django.conf import settings

from ..models import DocumentType

from .literals import (
    TEST_DOCUMENT_TYPE_LABEL, TEST_DOCUMENT_TYPE_QUICK_LABEL,
    TEST_DOCUMENT_TYPE_RANDOM_LABEL_LENGTH, TEST_SMALL_DOCUMENT_FILENAME
)

__all__ = ('DocumentTestMixin',)


class DocumentTestMixin(object):
    auto_create_document_type = True
    auto_upload_document = True
    test_document_filename = TEST_SMALL_DOCUMENT_FILENAME
    test_document_path = None
    use_document_stub = False

    @staticmethod
    def _get_random_alphanumeric_string(length):
        return ''.join(
            [random.choice(string.ascii_letters + string.digits) for _ in range(length)]
        )

    def _create_document_type(self):
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )
        self.test_document_type = self.document_type

    def _create_document_type_random(self):
        self.document_type = DocumentType.objects.create(
            label=DocumentTestMixin._get_random_alphanumeric_string(
                length=TEST_DOCUMENT_TYPE_RANDOM_LABEL_LENGTH
            )
        )
        self.test_document_type = self.document_type

    def _create_document(self, *args, **kwargs):
        """
        Alias for upload_document()
        """
        self.test_document = self.upload_document(*args, **kwargs)

    def _create_document_version(self):
        # Needed by MySQL as timestamp value doesn't include milliseconds
        # resolution
        time.sleep(1.01)

        self._calculate_test_document_path()

        with open(self.test_document_path, mode='rb') as file_object:
            self.test_document.new_version(file_object=file_object)

    def _calculate_test_document_path(self):
        if not self.test_document_path:
            self.test_document_path = os.path.join(
                settings.BASE_DIR, 'apps', 'documents', 'tests', 'contrib',
                'sample_documents', self.test_document_filename
            )

    def setUp(self):
        super(DocumentTestMixin, self).setUp()

        if self.auto_create_document_type:
            self._create_document_type()

            if self.auto_upload_document:
                self.document = self.upload_document()
                self.test_document = self.document

    def tearDown(self):
        for document_type in DocumentType.objects.all():
            document_type.delete()
        super(DocumentTestMixin, self).tearDown()

    def upload_document(self, document_type=None, filename=None):
        self._calculate_test_document_path()

        document_type = document_type or self.document_type

        if self.use_document_stub:
            document = document_type.documents.create(
                label=filename or self.test_document_filename
            )
        else:
            with open(self.test_document_path, mode='rb') as file_object:
                document = document_type.new_document(
                    file_object=file_object,
                    label=filename or self.test_document_filename
                )

        return document


class DocumentTypeQuickLabelTestMixin(object):
    def _create_quick_label(self):
        self.document_type_filename = self.document_type.filenames.create(
            filename=TEST_DOCUMENT_TYPE_QUICK_LABEL
        )

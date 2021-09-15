from __future__ import unicode_literals

from ..models import Index

from .literals import (
    TEST_INDEX_LABEL, TEST_INDEX_TEMPLATE_DOCUMENT_LABEL_EXPRESSION
)


class IndexTemplateTestMixin(object):
    def _create_index_template(self, add_document_type=False):
        # Create empty index
        self.test_index_template = Index.objects.create(label=TEST_INDEX_LABEL)

        if add_document_type:
            # Add our document type to the new index
            self.test_index_template.document_types.add(self.test_document_type)

    def _create_index_template_node(self, expression=None, rebuild=False):
        self._create_index_template(add_document_type=True)

        expression = expression or TEST_INDEX_TEMPLATE_DOCUMENT_LABEL_EXPRESSION

        self.test_index_template_node = self.test_index_template.node_templates.create(
            parent=self.test_index_template.template_root,
            expression=expression, link_documents=True
        )

        # Rebuild indexes
        if rebuild:
            Index.objects.rebuild()

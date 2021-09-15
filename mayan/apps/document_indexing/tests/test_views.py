from __future__ import absolute_import, unicode_literals

from mayan.apps.documents.permissions import (
    permission_document_view, permission_document_type_view
)
from mayan.apps.documents.tests import GenericDocumentViewTestCase

from ..models import Index
from ..permissions import (
    permission_document_indexing_create, permission_document_indexing_delete,
    permission_document_indexing_edit,
    permission_document_indexing_instance_view,
    permission_document_indexing_rebuild, permission_document_indexing_view
)

from .literals import (
    TEST_INDEX_LABEL, TEST_INDEX_LABEL_EDITED, TEST_INDEX_SLUG,
    TEST_INDEX_TEMPLATE_DOCUMENT_UUID_EXPRESSION,
    TEST_INDEX_TEMPLATE_NODE_EXPRESSION_EDITED
)
from .mixins import IndexTemplateTestMixin


class IndexInstanceViewTestCase(IndexTemplateTestMixin, GenericDocumentViewTestCase):
    def _request_index_instance_list_view(self):
        return self.get(
            viewname='indexing:index_instance_list',
        )

    def test_index_instance_list_view_no_permission(self):
        self._create_index_template_node()

        response = self._request_index_instance_list_view()

        self.assertNotContains(
            response=response, text=TEST_INDEX_LABEL, status_code=200
        )

    def test_index_instance_list_view_with_access(self):
        self._create_index_template_node(rebuild=True)

        self.grant_access(
            obj=self.test_index_template,
            permission=permission_document_indexing_instance_view
        )

        response = self._request_index_instance_list_view()

        self.assertContains(
            response=response, text=TEST_INDEX_LABEL, status_code=200
        )

    def _request_index_instance_node_view(self, index_instance_node=None):
        index_instance_node = index_instance_node or self.test_index_template.instance_root

        return self.get(
            viewname='indexing:index_instance_node_view',
            kwargs={
                'index_instance_node_id': index_instance_node.pk
            }
        )

    def test_index_instance_node_view_no_permission(self):
        self._create_index_template_node()

        response = self._request_index_instance_node_view()

        self.assertEqual(response.status_code, 404)

    def test_index_instance_node_view_with_access(self):
        self._create_index_template_node()

        self.grant_access(
            obj=self.test_index_template,
            permission=permission_document_indexing_instance_view
        )

        response = self._request_index_instance_node_view()

        self.assertContains(
            response=response, text=TEST_INDEX_LABEL, status_code=200
        )

    def _test_index_instance_node_documents_view_base(self, index_access=False, document_access=False):
        self._create_index_template_node(
            expression=TEST_INDEX_TEMPLATE_DOCUMENT_UUID_EXPRESSION,
            rebuild=True
        )

        if index_access:
            self.grant_access(
                obj=self.test_index_template,
                permission=permission_document_indexing_instance_view
            )

        if document_access:
            self.grant_access(
                obj=self.test_document,
                permission=permission_document_view
            )

        index_instance_node = self.test_index_template.instance_root.get_children().get(
            value=self.test_document.uuid
        )

        return self._request_index_instance_node_view(
            index_instance_node=index_instance_node
        )

    def test_index_instance_node_documents_view_no_permission(self):
        response = self._test_index_instance_node_documents_view_base()

        self.assertNotContains(
            response=response, text=TEST_INDEX_LABEL, status_code=404
        )
        self.assertNotContains(
            response=response, text=self.test_document.label, status_code=404
        )

    def test_index_instance_node_documents_view_with_index_access(self):
        response = self._test_index_instance_node_documents_view_base(
            index_access=True
        )

        self.assertContains(
            response=response, text=TEST_INDEX_LABEL, status_code=200
        )
        self.assertNotContains(
            response=response, text=self.test_document.label, status_code=200
        )

    def test_index_instance_node_documents_view_with_document_access(self):
        response = self._test_index_instance_node_documents_view_base(
            document_access=True
        )

        self.assertNotContains(
            response=response, text=TEST_INDEX_LABEL, status_code=404
        )
        self.assertNotContains(
            response=response, text=self.test_document.label, status_code=404
        )

    def test_index_instance_node_documents_view_with_full_access(self):
        response = self._test_index_instance_node_documents_view_base(
            index_access=True, document_access=True
        )

        self.assertContains(
            response=response, text=TEST_INDEX_LABEL, status_code=200
        )
        self.assertContains(
            response=response, text=self.test_document.label, status_code=200
        )

    def _request_index_instances_rebuild_get_view(self):
        return self.get(
            viewname='indexing:index_instances_rebuild',
        )

    def _request_index_instances_rebuild_post_view(self):
        return self.post(
            viewname='indexing:index_instances_rebuild', data={
                'index_templates': self.test_index_template.pk
            }
        )

    def test_index_instances_rebuild_get_view_no_permission(self):
        self._create_index_template_node(rebuild=False)

        response = self._request_index_instances_rebuild_get_view()
        self.assertNotContains(
            response=response, text=self.test_index_template.label, status_code=200
        )

    def test_index_instances_rebuild_get_view_with_access(self):
        self._create_index_template_node(rebuild=False)

        self.grant_access(
            obj=self.test_index_template, permission=permission_document_indexing_rebuild
        )

        response = self._request_index_instances_rebuild_get_view()
        self.assertContains(
            response=response, text=self.test_index_template.label, status_code=200
        )

    def test_index_instances_rebuild_post_view_no_permission(self):
        self._create_index_template_node(rebuild=False)

        response = self._request_index_instances_rebuild_post_view()
        # No error since we just don't see the index
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            self.test_index_template.instance_root.get_children_count(), 0
        )

    def test_index_instances_rebuild_post_view_with_access(self):
        self._create_index_template_node(rebuild=False)

        self.grant_access(
            obj=self.test_index_template, permission=permission_document_indexing_rebuild
        )

        response = self._request_index_instances_rebuild_post_view()
        self.assertEqual(response.status_code, 302)

        # An instance root exists
        self.assertTrue(self.test_index_template.instance_root.pk)


class IndexTemplateViewTestCase(IndexTemplateTestMixin, GenericDocumentViewTestCase):
    auto_create_document_type = False
    auto_upload_document = False

    def _request_index_create_view(self):
        return self.post(
            'indexing:index_template_create', data={
                'label': TEST_INDEX_LABEL, 'slug': TEST_INDEX_SLUG
            }
        )

    def test_index_create_view_no_permission(self):
        response = self._request_index_create_view()
        self.assertEquals(response.status_code, 403)

        self.assertEqual(Index.objects.count(), 0)

    def test_index_create_view_with_permission(self):
        self.grant_permission(
            permission=permission_document_indexing_create
        )

        response = self._request_index_create_view()

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Index.objects.count(), 1)
        self.assertEqual(Index.objects.first().label, TEST_INDEX_LABEL)

    def _request_index_template_delete_view(self):
        return self.post(
            viewname='indexing:index_template_delete',
            kwargs={'index_template_id': self.test_index_template.pk}
        )

    def test_index_template_delete_view_no_permission(self):
        self._create_index_template()

        response = self._request_index_template_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(Index.objects.count(), 1)

    def test_index_template_delete_view_with_access(self):
        self._create_index_template()

        self.grant_access(
            obj=self.test_index_template,
            permission=permission_document_indexing_delete
        )
        response = self._request_index_template_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Index.objects.count(), 0)

    def _request_index_template_document_types_view(self):
        return self.post(
            viewname='indexing:index_template_document_types',
            kwargs={'index_template_id': self.test_index_template.pk}
        )

    def test_index_template_document_types_view_no_permission(self):
        self._create_document_type()
        self._create_index_template()

        response = self._request_index_template_document_types_view()
        self.assertEqual(response.status_code, 404)

    def test_index_template_document_types_view_with_index_access(self):
        self._create_document_type()
        self._create_index_template()

        self.grant_access(
            obj=self.test_index_template,
            permission=permission_document_indexing_edit
        )
        response = self._request_index_template_document_types_view()
        self.assertNotContains(
            response=response, text=self.document_type.label, status_code=200
        )

    def test_index_template_document_types_view_with_document_type_access(self):
        self._create_document_type()
        self._create_index_template()

        self.grant_access(
            obj=self.test_document_type,
            permission=permission_document_type_view
        )
        response = self._request_index_template_document_types_view()
        self.assertEqual(response.status_code, 404)

    def test_index_template_document_types_view_with_full_access(self):
        self._create_document_type()
        self._create_index_template()

        self.grant_access(
            obj=self.test_index_template,
            permission=permission_document_indexing_edit
        )
        self.grant_access(
            obj=self.test_document_type,
            permission=permission_document_type_view
        )
        response = self._request_index_template_document_types_view()
        self.assertContains(
            response=response, text=self.document_type.label, status_code=200
        )

    def _request_index_edit_view(self):
        return self.post(
            viewname='indexing:index_template_edit', kwargs={
                'index_template_id': self.test_index_template.pk
            }, data={
                'label': TEST_INDEX_LABEL_EDITED, 'slug': TEST_INDEX_SLUG
            }
        )

    def test_index_edit_view_no_permission(self):
        self._create_index_template()

        response = self._request_index_edit_view()
        self.assertEqual(response.status_code, 404)

        self.test_index_template.refresh_from_db()
        self.assertEqual(self.test_index_template.label, TEST_INDEX_LABEL)

    def test_index_edit_view_with_access(self):
        self._create_index_template()

        self.grant_access(
            obj=self.test_index_template,
            permission=permission_document_indexing_edit
        )

        response = self._request_index_edit_view()
        self.assertEqual(response.status_code, 302)

        self.test_index_template.refresh_from_db()
        self.assertEqual(self.test_index_template.label, TEST_INDEX_LABEL_EDITED)

    def _request_index_template_list_view(self):
        return self.get(viewname='indexing:index_template_list')

    def test_index_template_list_view_no_permission(self):
        self._create_index_template()

        response = self._request_index_template_list_view()
        self.assertNotContains(
            response=response, text=self.test_index_template.label, status_code=200
        )

    def test_index_template_list_view_with_access(self):
        self._create_index_template()

        self.grant_access(
            obj=self.test_index_template,
            permission=permission_document_indexing_view
        )

        response = self._request_index_template_list_view()
        self.assertContains(
            response=response, text=self.test_index_template.label, status_code=200
        )


class IndexTemplaceNodeViewTestCase(IndexTemplateTestMixin, GenericDocumentViewTestCase):
    auto_upload_document = False

    def _request_index_instance_node_delete_view(self):
        return self.post(
            viewname='indexing:index_template_node_delete', kwargs={
                'index_template_node_id': self.test_index_template_node.pk
            }
        )

    def test_index_template_node_delete_view_no_permission(self):
        self._create_index_template_node()

        response = self._request_index_instance_node_delete_view()

        self.assertEqual(response.status_code, 404)

        # Root node plus the defaul test document label node
        self.assertEqual(self.test_index_template.node_templates.count(), 2)

    def test_index_template_node_delete_view_with_access(self):
        self._create_index_template_node()

        self.grant_access(
            obj=self.test_index_template,
            permission=permission_document_indexing_edit
        )

        response = self._request_index_instance_node_delete_view()

        self.assertEqual(response.status_code, 302)

        # Root node only
        self.assertEqual(self.test_index_template.node_templates.count(), 1)

    def _request_index_instance_node_edit_view(self):
        return self.post(
            viewname='indexing:index_template_node_edit', kwargs={
                'index_template_node_id': self.test_index_template_node.pk
            }, data={
                'expression': TEST_INDEX_TEMPLATE_NODE_EXPRESSION_EDITED,
                'index': self.test_index_template.pk,
                'parent': self.test_index_template_node.parent.pk,

            }
        )

    def test_index_template_node_edit_view_no_permission(self):
        self._create_index_template_node()
        original_expression = self.test_index_template_node.expression

        response = self._request_index_instance_node_edit_view()
        self.assertEqual(response.status_code, 404)

        self.test_index_template_node.refresh_from_db()
        self.assertEqual(
            self.test_index_template_node.expression, original_expression
        )

    def test_index_template_node_edit_view_with_access(self):
        self._create_index_template_node()
        self.grant_access(
            obj=self.test_index_template,
            permission=permission_document_indexing_edit
        )

        response = self._request_index_instance_node_edit_view()
        self.assertEqual(response.status_code, 302)

        self.test_index_template_node.refresh_from_db()
        self.assertEqual(
            self.test_index_template_node.expression,
            TEST_INDEX_TEMPLATE_NODE_EXPRESSION_EDITED
        )

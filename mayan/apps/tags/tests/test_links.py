from __future__ import unicode_literals

from django.urls import reverse

from mayan.apps.documents.tests import GenericDocumentViewTestCase

from ..links import link_document_tag_list
from ..permissions import permission_tag_view

from .mixins import TagTestMixin


class DocumentLinksTestCase(TagTestMixin, GenericDocumentViewTestCase):
    def _request_document_tag_list_link(self):
        self.add_test_view(test_object=self.document)
        context = self.get_test_view()
        return link_document_tag_list.resolve(context=context)

    def test_document_tag_list_no_permission(self):
        self._create_test_tag()
        resolved_link = self._request_document_tag_list_link()
        self.assertEqual(resolved_link, None)

    def test_document_tag_list_with_full_access(self):
        self._create_test_tag()
        self.grant_access(
            obj=self.document, permission=permission_tag_view
        )
        self.grant_access(
            obj=self.test_tag, permission=permission_tag_view
        )
        resolved_link = self._request_document_tag_list_link()

        self.assertNotEqual(resolved_link, None)
        self.assertEqual(
            resolved_link.url,
            reverse(
                viewname='tags:document_tag_list',
                kwargs={'document_id': self.document.pk}
            )
        )

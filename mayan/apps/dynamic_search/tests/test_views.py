from __future__ import unicode_literals

from mayan.apps.common.tests import GenericViewTestCase
from mayan.apps.documents.search import document_search
from mayan.apps.documents.tests import DocumentTestMixin


class Issue46TestCase(DocumentTestMixin, GenericViewTestCase):
    """
    Functional tests to make sure issue 46 is fixed
    """
    auto_upload_document = False
    auto_login_superuser = True
    create_test_case_superuser = True
    create_test_case_user = False

    def setUp(self):
        super(Issue46TestCase, self).setUp()

        self.document_count = 4

        # Upload many instances of the same test document
        for i in range(self.document_count):
            self.test_document = self.upload_document()

    def test_advanced_search_past_first_page(self):
        # Make sure all documents are returned by the search
        queryset = document_search.search(
            {'label': self.test_document.label}, user=self._test_case_superuser
        )
        self.assertEqual(queryset.count(), self.document_count)

        with self.settings(COMMON_PAGINATE_BY=2):
            # Functional test for the first page of advanced results
            response = self.get(
                viewname='search:results',
                kwargs={'search_model': document_search.get_full_name()},
                data={'label': 'test'}
            )

            # Total (1 - 2 out of 4) (Page 1 of 2)
            # 4 results total, 2 pages, current page is 1,
            # object in this page: 2
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.context['paginator'].object_list.count(), 4
            )
            self.assertEqual(response.context['paginator'].num_pages, 2)
            self.assertEqual(response.context['page_obj'].number, 1)
            self.assertEqual(
                response.context['page_obj'].object_list.count(), 2
            )

            # Functional test for the second page of advanced results
            response = self.get(
                viewname='search:results',
                kwargs={'search_model': document_search.get_full_name()},
                data={'label': 'test', 'page': 2}
            )

            # Total (3 - 4 out of 4) (Page 2 of 2)
            # 4 results total, 2 pages, current page is 1,
            # object in this page: 2
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.context['paginator'].object_list.count(), 4
            )
            self.assertEqual(response.context['paginator'].num_pages, 2)
            self.assertEqual(response.context['page_obj'].number, 2)
            self.assertEqual(
                response.context['page_obj'].object_list.count(), 2
            )

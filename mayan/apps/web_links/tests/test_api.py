from rest_framework import status

from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests.base import DocumentTestMixin
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..models import WebLink
from ..permissions import (
    permission_web_link_create, permission_web_link_delete,
    permission_web_link_edit, permission_web_link_view
)

from .literals import (
    TEST_WEB_LINK_LABEL_EDITED, TEST_WEB_LINK_LABEL, TEST_WEB_LINK_TEMPLATE
)
from .mixins import WebLinkTestMixin


class WebLinkAPIViewTestMixin(object):
    def _request_test_web_link_create_api_view(self):
        return self.post(
            viewname='rest_api:web_link-list', data={
                'label': TEST_WEB_LINK_LABEL,
                'template': TEST_WEB_LINK_TEMPLATE
            }
        )

    def _request_test_web_link_create_with_document_type_api_view(self):
        return self.post(
            viewname='rest_api:web_link-list', data={
                'label': TEST_WEB_LINK_LABEL,
                'document_types_pk_list': self.test_document_type.pk,
                'template': TEST_WEB_LINK_TEMPLATE
            },
        )

    def _request_test_web_link_delete_api_view(self):
        return self.delete(
            viewname='rest_api:web_link-detail', kwargs={
                'pk': self.test_web_link.pk
            }
        )

    def _request_test_web_link_detail_api_view(self):
        return self.get(
            viewname='rest_api:web_link-detail', kwargs={
                'pk': self.test_web_link.pk
            }
        )

    def _request_test_web_link_edit_patch_api_view(self):
        return self.patch(
            viewname='rest_api:web_link-detail',
            kwargs={'pk': self.test_web_link.pk}, data={
                'label': TEST_WEB_LINK_LABEL_EDITED,
                'document_types_pk_list': self.test_document_type.pk
            }
        )

    def _request_test_web_link_edit_put_api_view(self):
        return self.put(
            viewname='rest_api:web_link-detail',
            kwargs={'pk': self.test_web_link.pk}, data={
                'label': TEST_WEB_LINK_LABEL_EDITED,
                'document_types_pk_list': self.test_document_type.pk,
                'template': TEST_WEB_LINK_TEMPLATE
            }
        )


class WebLinkAPIViewTestCase(
    DocumentTestMixin, WebLinkTestMixin, WebLinkAPIViewTestMixin,
    BaseAPITestCase
):
    auto_create_test_document_type = False
    auto_upload_test_document = False

    def test_web_link_create_view_no_permission(self):
        response = self._request_test_web_link_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(WebLink.objects.count(), 0)

    def test_web_link_create_view_with_permission(self):
        self.grant_permission(permission=permission_web_link_create)

        response = self._request_test_web_link_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        web_link = WebLink.objects.first()
        self.assertEqual(response.data['id'], web_link.pk)
        self.assertEqual(response.data['label'], TEST_WEB_LINK_LABEL)

        self.assertEqual(WebLink.objects.count(), 1)
        self.assertEqual(web_link.label, TEST_WEB_LINK_LABEL)

    def test_web_link_create_with_document_types_view_no_permission(self):
        self._create_test_document_type()

        response = self._request_test_web_link_create_with_document_type_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(WebLink.objects.count(), 0)

    def test_web_link_create_with_document_types_view_with_permission(self):
        self._create_test_document_type()
        self.grant_permission(permission=permission_web_link_create)

        response = self._request_test_web_link_create_with_document_type_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        web_link = WebLink.objects.first()
        self.assertEqual(response.data['id'], web_link.pk)
        self.assertEqual(response.data['label'], TEST_WEB_LINK_LABEL)

        self.assertEqual(WebLink.objects.count(), 1)
        self.assertEqual(web_link.label, TEST_WEB_LINK_LABEL)
        self.assertTrue(
            self.test_document_type in web_link.document_types.all()
        )

    def test_web_link_delete_view_no_permission(self):
        self._create_test_web_link()

        response = self._request_test_web_link_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(WebLink.objects.count(), 1)

    def test_web_link_delete_view_with_access(self):
        self._create_test_web_link()
        self.grant_access(
            obj=self.test_web_link, permission=permission_web_link_delete
        )

        response = self._request_test_web_link_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(WebLink.objects.count(), 0)

    def test_web_link_detail_view_no_permission(self):
        self._create_test_web_link()

        response = self._request_test_web_link_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertFalse('label' in response.data)

    def test_web_link_detail_view_with_access(self):
        self._create_test_web_link()
        self.grant_access(
            obj=self.test_web_link, permission=permission_web_link_view
        )

        response = self._request_test_web_link_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data['label'], TEST_WEB_LINK_LABEL
        )

    def test_web_link_edit_view_via_patch_no_permission(self):
        self._create_test_document_type()
        self._create_test_web_link()

        response = self._request_test_web_link_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_web_link.refresh_from_db()
        self.assertEqual(self.test_web_link.label, TEST_WEB_LINK_LABEL)

    def test_web_link_edit_view_via_patch_with_access(self):
        self._create_test_document_type()
        self._create_test_web_link()
        self.grant_access(
            obj=self.test_web_link, permission=permission_web_link_edit
        )

        response = self._request_test_web_link_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_web_link.refresh_from_db()
        self.assertEqual(
            self.test_web_link.label, TEST_WEB_LINK_LABEL_EDITED
        )

    def test_web_link_edit_view_via_put_no_permission(self):
        self._create_test_document_type()
        self._create_test_web_link()

        response = self._request_test_web_link_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_web_link.refresh_from_db()
        self.assertEqual(self.test_web_link.label, TEST_WEB_LINK_LABEL)

    def test_web_link_edit_view_via_put_with_access(self):
        self._create_test_document_type()
        self._create_test_web_link()
        self.grant_access(
            obj=self.test_web_link, permission=permission_web_link_edit
        )

        response = self._request_test_web_link_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_web_link.refresh_from_db()
        self.assertEqual(
            self.test_web_link.label, TEST_WEB_LINK_LABEL_EDITED
        )

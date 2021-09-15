from __future__ import unicode_literals

from django.test import override_settings

from mayan.apps.rest_api.tests import BaseAPITestCase

from ..classes import Template

TEST_TEMPLATE_RESULT = '<div'


class CommonAPITestCase(BaseAPITestCase):
    auto_login_user = False

    def test_content_type_list_view(self):
        response = self.get(viewname='rest_api:content_type-list')
        self.assertEqual(response.status_code, 200)

    def _request_template_detail_view(self):
        return self.get(path=self.test_template.get_absolute_url())

    def test_template_detail_view(self):
        self.login_user()

        self.test_template = Template.get(name='menu_main')

        response = self._request_template_detail_view()
        self.assertContains(
            response=response, text=TEST_TEMPLATE_RESULT, status_code=200
        )

    @override_settings(LANGUAGE_CODE='de')
    def test_template_detail_german_view(self):
        self.login_user()

        self.test_template = Template.get(name='menu_main')

        response = self._request_template_detail_view()
        self.assertContains(
            response=response, text=TEST_TEMPLATE_RESULT, status_code=200
        )

    def test_template_detail_anonymous_view(self):
        self.test_template = Template.get(name='menu_main')

        response = self._request_template_detail_view()
        self.assertNotContains(
            response=response, text=TEST_TEMPLATE_RESULT, status_code=403
        )

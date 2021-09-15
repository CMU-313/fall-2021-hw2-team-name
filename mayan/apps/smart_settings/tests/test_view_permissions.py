from __future__ import absolute_import, unicode_literals

from mayan.apps.common.tests import GenericViewTestCase

from ..permissions import permission_settings_view


class SmartSettingViewPermissionsTestCase(GenericViewTestCase):
    def test_view_access_denied(self):
        response = self.get(viewname='settings:namespace_list')

        self.assertEqual(response.status_code, 403)

        response = self.get(
            viewname='settings:namespace_detail',
            kwargs={'namespace_name': 'common'}
        )
        self.assertEqual(response.status_code, 403)

    def test_view_access_permitted(self):
        self.grant_permission(permission=permission_settings_view)

        response = self.get(viewname='settings:namespace_list')
        self.assertEqual(response.status_code, 200)

        response = self.get(
            viewname='settings:namespace_detail',
            kwargs={'namespace_name': 'common'}
        )
        self.assertEqual(response.status_code, 200)

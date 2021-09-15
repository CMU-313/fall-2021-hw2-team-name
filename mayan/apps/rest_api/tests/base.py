from __future__ import absolute_import, unicode_literals

from rest_framework.test import APITestCase

from mayan.apps.common.tests import GenericViewTestCase
from mayan.apps.permissions.classes import Permission
from mayan.apps.smart_settings.classes import Namespace


class BaseAPITestCase(APITestCase, GenericViewTestCase):
    """
    API test case class that invalidates permissions and smart settings
    """
    expected_content_type = 'application/json'

    def setUp(self):
        super(BaseAPITestCase, self).setUp()
        Namespace.invalidate_cache_all()
        Permission.invalidate_cache()

    def tearDown(self):
        super(BaseAPITestCase, self).tearDown()

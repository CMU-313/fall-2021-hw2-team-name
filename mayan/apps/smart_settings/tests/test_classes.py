from __future__ import absolute_import, unicode_literals

import os

import yaml

from django.conf import settings

from mayan.apps.common.settings import setting_paginate_by
from mayan.apps.common.tests import BaseTestCase
from mayan.apps.storage.utils import fs_cleanup, mkstemp

from .literals import TEST_SETTING_NAME, TEST_SETTING_VALUE


class ClassesTestCase(BaseTestCase):
    def test_config_file(self):
        test_config_file_descriptor, test_config_filename = mkstemp()
        with open(test_config_filename, mode='w') as file_object:
            file_object.write(
                yaml.safe_dump(
                    {TEST_SETTING_NAME: TEST_SETTING_VALUE}
                )
            )

        settings.CONFIGURATION_FILEPATH = test_config_filename
        setting_value = setting_paginate_by.value
        fs_cleanup(filename=test_config_filename)

        self.assertEqual(setting_value, TEST_SETTING_VALUE)

    def test_environment_variable(self):
        os.environ['MAYAN_{}'.format(TEST_SETTING_NAME)] = '{}'.format(
            TEST_SETTING_VALUE
        )

        setting_value = setting_paginate_by.value
        os.environ.pop('MAYAN_{}'.format(TEST_SETTING_NAME))
        self.assertEqual(setting_value, TEST_SETTING_VALUE)

from __future__ import unicode_literals

from mayan.apps.common import MayanAppConfig


class FileCachingConfig(MayanAppConfig):
    has_tests = False
    name = 'mayan.apps.file_caching'

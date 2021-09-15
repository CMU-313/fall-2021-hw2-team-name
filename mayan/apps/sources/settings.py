from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings import Namespace

from .literals import (
    DEFAULT_SCANIMAGE_PATH, DEFAULT_STAGING_FILE_CACHE_STORAGE_BACKEND,
    DEFAULT_STAGING_FILE_CACHE_STORAGE_BACKEND_ARGUMENTS
)

namespace = Namespace(label=_('Sources'), name='sources')

setting_scanimage_path = namespace.add_setting(
    global_name='SOURCES_SCANIMAGE_PATH', default=DEFAULT_SCANIMAGE_PATH,
    help_text=_(
        'File path to the scanimage program used to control image scanners.'
    )
)
setting_staging_file_image_cache_storage = namespace.add_setting(
    global_name=DEFAULT_STAGING_FILE_CACHE_STORAGE_BACKEND,
    default='django.core.files.storage.FileSystemStorage', help_text=_(
        'Path to the Storage subclass to use when storing the cached '
        'staging_file image files.'
    )
)
setting_staging_file_image_cache_storage_arguments = namespace.add_setting(
    global_name='SOURCES_STAGING_FILE_CACHE_STORAGE_BACKEND_ARGUMENTS',
    default=DEFAULT_STAGING_FILE_CACHE_STORAGE_BACKEND_ARGUMENTS, help_text=_(
        'Arguments to pass to the SOURCES_STAGING_FILE_CACHE_STORAGE_BACKEND.'
    )
)

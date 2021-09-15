from __future__ import unicode_literals

from django.utils.module_loading import import_string

from mayan.apps.common.utils import get_storage_subclass

from .settings import (
    setting_storage_backend, setting_storage_backend_arguments
)

storage_detachedsignature = get_storage_subclass(
    dotted_path=setting_storage_backend.value
)(**setting_storage_backend_arguments.value)

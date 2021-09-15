from __future__ import unicode_literals

from .settings import setting_shared_storage, setting_shared_storage_arguments
from .utils import get_storage_subclass

storage_sharedupload = get_storage_subclass(
    dotted_path=setting_shared_storage.value
)(**setting_shared_storage_arguments.value)

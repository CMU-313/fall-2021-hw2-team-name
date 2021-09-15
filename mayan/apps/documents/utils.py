from __future__ import unicode_literals

import hashlib
import uuid

from django.apps import apps
from django.utils.encoding import force_text

from .literals import DOCUMENT_IMAGES_CACHE_NAME


def callback_update_cache_size(setting):
    Cache = apps.get_model(app_label='common', model_name='Cache')
    cache = Cache.objects.get(name=DOCUMENT_IMAGES_CACHE_NAME)
    cache.maximum_size = setting.value
    cache.save()


def document_hash_function(data):
    return hashlib.sha256(data).hexdigest()


def document_uuid_function(*args, **kwargs):
    return force_text(uuid.uuid4())


def parse_range(astr):
    # http://stackoverflow.com/questions/4248399/
    # page-range-for-printing-algorithm
    result = set()
    for part in astr.split(','):
        x = part.split('-')
        result.update(range(int(x[0]), int(x[-1]) + 1))
    return sorted(result)

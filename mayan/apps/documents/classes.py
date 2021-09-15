from __future__ import absolute_import, unicode_literals

import uuid

from django.utils.translation import ugettext_lazy as _


class BaseDocumentFilenameGenerator(object):
    _registry = {}

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def get_choices(cls):
        return sorted(
            [
                (name, klass.label) for name, klass in cls._registry.items()
            ]
        )

    @classmethod
    def register(cls, klass):
        cls._registry[klass.name] = klass

    def upload_to(self, instance, filename):
        raise NotImplementedError


class UUIDDocumentFilenameGenerator(BaseDocumentFilenameGenerator):
    name = 'uuid'
    label = _('UUID')

    def upload_to(self, instance, filename):
        return force_text(uuid.uuid4())


BaseDocumentFilenameGenerator.register(klass=UUIDDocumentFilenameGenerator)

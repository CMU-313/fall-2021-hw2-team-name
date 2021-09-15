from __future__ import unicode_literals

from ..models import Cabinet

from .literals import TEST_CABINET_LABEL


class CabinetTestMixin(object):
    def _create_cabinet(self):
        self.cabinet = Cabinet.objects.create(label=TEST_CABINET_LABEL)

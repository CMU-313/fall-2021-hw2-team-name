from __future__ import unicode_literals

from ..models import SmartLink

from .literals import TEST_SMART_LINK_DYNAMIC_LABEL, TEST_SMART_LINK_LABEL


class SmartLinkTestMixin(object):
    def _create_test_smart_link(self):
        self.test_smart_link = SmartLink.objects.create(
            label=TEST_SMART_LINK_LABEL,
            dynamic_label=TEST_SMART_LINK_DYNAMIC_LABEL
        )

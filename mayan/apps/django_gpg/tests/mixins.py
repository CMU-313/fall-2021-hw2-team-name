from ..models import Key

from .literals import TEST_KEY_DATA


class KeyTestMixin(object):
    def _create_test_key(self):
        # Creating a Key instance is analogous to importing a key
        self.test_key = Key.objects.create(key_data=TEST_KEY_DATA)

from __future__ import absolute_import, unicode_literals

import random
import time

from .exceptions import LockError


def retry_on_lock_error(retries):
    def decorator(function):
        def wrapper():
            retry_count = 0

            while True:
                try:
                    return function()
                except LockError:
                    if retry_count == retries:
                        raise
                    else:
                        retry_count = retry_count + 1
                        timeout = 2 ** retry_count
                        timeout = random.randrange(timeout + 1)
                        time.sleep(timeout)
        return wrapper
    return decorator

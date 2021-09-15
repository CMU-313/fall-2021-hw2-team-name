from __future__ import unicode_literals


class LockError(Exception):
    """Raised when trying to acquire an existing lock"""

from __future__ import unicode_literals


class PermissionError(Exception):
    """Base permission exception"""


class InvalidNamespace(PermissionError):
    """
    Invalid namespace name. This is probably an obsolete permission namespace,
    execute the management command "purgepermissions" and try again.
    """

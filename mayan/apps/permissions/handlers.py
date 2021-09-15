from __future__ import unicode_literals

from django.core import management


def handler_purge_permissions(**kwargs):
    management.call_command('purgepermissions')

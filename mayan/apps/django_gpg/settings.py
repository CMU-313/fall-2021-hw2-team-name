from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings import Namespace

from .literals import (
    DEFAULT_GPG_PATH, DEFAULT_KEYSERVER, DEFAULT_SETTING_GPG_BACKEND
)

namespace = Namespace(label=_('Signatures'), name='django_gpg')

setting_gpg_backend = namespace.add_setting(
    default=DEFAULT_SETTING_GPG_BACKEND,
    global_name='SIGNATURES_GPG_BACKEND', help_text=_(
        'Path to the GPG class to use when managing keys.'
    )
)
setting_gpg_backend_arguments = namespace.add_setting(
    global_name='SIGNATURES_GPG_BACKEND_ARGUMENTS',
    default={
        'gpg_path': DEFAULT_GPG_PATH
    }, help_text=_(
        'Arguments to pass to the SIGNATURES_GPG_BACKEND. '
    )
)
setting_keyserver = namespace.add_setting(
    global_name='SIGNATURES_KEYSERVER', default=DEFAULT_KEYSERVER,
    help_text=_('Keyserver used to query for keys.')
)

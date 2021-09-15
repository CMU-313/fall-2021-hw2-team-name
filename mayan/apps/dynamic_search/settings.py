from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings import Namespace

namespace = Namespace(label=_('Search'), name='dynamic_search')

setting_limit = namespace.add_setting(
    global_name='SEARCH_LIMIT', default=100,
    help_text=_('Maximum amount search hits to fetch and display.')
)

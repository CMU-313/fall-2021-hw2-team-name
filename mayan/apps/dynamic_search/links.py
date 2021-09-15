from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation import Link

link_search = Link(
    kwargs={'search_model': 'search_model.get_full_name'}, text=_('Search'),
    view='search:search'
)
link_search_advanced = Link(
    kwargs={'search_model': 'search_model.get_full_name'},
    text=_('Advanced search'), view='search:search_advanced'
)
link_search_again = Link(
    kwargs={'search_model': 'search_model.get_full_name'}, keep_query=True,
    text=_('Search again'), view='search:search_again'
)

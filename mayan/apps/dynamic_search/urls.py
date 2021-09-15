from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import SearchModelAPIViewSet
from .views import AdvancedSearchView, ResultsView, SearchAgainView, SearchView

urlpatterns = [
    url(
        regex=r'^(?P<search_model>[\.\w]+)/$', name='search',
        view=SearchView.as_view()
    ),
    url(
        regex=r'^advanced/(?P<search_model>[\.\w]+)/$', name='search_advanced',
        view=AdvancedSearchView.as_view()
    ),
    url(
        regex=r'^again/(?P<search_model>[\.\w]+)/$', name='search_again',
        view=SearchAgainView.as_view()
    ),
    url(
        regex=r'^results/(?P<search_model>[\.\w]+)/$', name='results',
        view=ResultsView.as_view()
    )
]

api_router_entries = (
    {
        'prefix': r'search_models', 'viewset': SearchModelAPIViewSet,
        'basename': 'search_model'
    },
)

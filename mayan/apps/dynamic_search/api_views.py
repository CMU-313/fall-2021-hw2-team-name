from __future__ import unicode_literals

from django.utils.encoding import force_text

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError

from mayan.apps.rest_api.viewsets import MayanAPIReadOnlyModelViewSet

from .classes import SearchModel
from .serializers import SearchModelSerializer


class SearchModelAPIViewSet(MayanAPIReadOnlyModelViewSet):
    lookup_field = 'name'
    lookup_url_kwarg = 'search_model_name'
    lookup_value_regex = r'[\w\.]+'
    serializer_class = SearchModelSerializer
    queryset = SearchModel.all()

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        return SearchModel.get(**filter_kwargs)

    @action(detail=True, url_name='search', url_path='search')
    def search(self, request, *args, **kwargs):
        search_model = self.get_object()

        # Override serializer class just before producing the queryset of
        # search results
        self.serializer_class = search_model.serializer

        if self.request.GET.get('_match_all', 'off') == 'on':
            global_and_search = True
        else:
            global_and_search = False

        try:
            queryset = search_model.search(
                global_and_search=global_and_search,
                query_string=self.request.GET, user=self.request.user
            )
        except Exception as exception:
            raise ParseError(force_text(exception))

        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(
            queryset, many=True, context={'request': request}
        )

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)

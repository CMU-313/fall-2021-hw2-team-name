from __future__ import unicode_literals

from rest_framework import serializers


class SearchFieldSerializer(serializers.Serializer):
    field = serializers.CharField(read_only=True)
    label = serializers.CharField(read_only=True)


class SearchModelSerializer(serializers.Serializer):
    app_label = serializers.CharField(read_only=True)
    model_name = serializers.CharField(read_only=True)
    pk = serializers.CharField(read_only=True)
    search_fields = SearchFieldSerializer(many=True, read_only=True)
    search_url = serializers.HyperlinkedIdentityField(
        lookup_field='pk',
        lookup_url_kwarg='search_model_name',
        view_name='rest_api:search_model-search'
    )
    url = serializers.HyperlinkedIdentityField(
        lookup_field='pk',
        lookup_url_kwarg='search_model_name',
        view_name='rest_api:search_model-detail'
    )

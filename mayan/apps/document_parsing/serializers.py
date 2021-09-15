from __future__ import unicode_literals

from rest_framework import serializers


class DocumentPageParsingSerializer(serializers.Serializer):
    text = serializers.CharField(
        read_only=True, source='get_content'
    )


class DocumentParsingSerializer(serializers.Serializer):
    text = serializers.CharField(
        read_only=True, source='get_content'
    )


class DocumentVersionParsingSerializer(serializers.Serializer):
    text = serializers.CharField(
        read_only=True, source='get_content'
    )

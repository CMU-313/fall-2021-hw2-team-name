from __future__ import unicode_literals

from rest_framework import serializers


class DocumentOCRSerializer(serializers.Serializer):
    text = serializers.CharField(
        read_only=True, source='get_ocr_content'
    )


class DocumentPageOCRContentSerializer(serializers.Serializer):
    text = serializers.CharField(
        read_only=True, source='get_ocr_content'
    )


class DocumentVersionOCRSerializer(serializers.Serializer):
    text = serializers.CharField(
        read_only=True, source='get_ocr_content'
    )

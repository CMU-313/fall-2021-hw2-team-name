from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from mayan.apps.documents.models import Document, DocumentVersion
from mayan.apps.rest_api.viewsets import MayanAPIViewSet, MayanAPIGenericViewSet

from .permissions import permission_ocr_content_view, permission_ocr_document
from .serializers import (
    DocumentOCRSerializer, DocumentPageOCRContentSerializer,
    DocumentVersionOCRSerializer
)


class DocumentOCRAPIViewSet(MayanAPIViewSet):
    lookup_url_kwarg = 'document_id'
    object_permission_map = {
        'ocr_content': permission_ocr_content_view,
        'ocr_submit': permission_ocr_document,
    }
    queryset = Document.objects.all()
    serializer_class = DocumentOCRSerializer

    @action(
        detail=True, url_name='content', url_path='ocr'
    )
    def ocr_content(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(data=serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    @action(
        detail=True, methods=('post',), url_name='submit',
        url_path='ocr/submit'
    )
    def ocr_submit(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.submit_for_ocr(_user=request.user)
        return Response(
            data=None, status=status.HTTP_202_ACCEPTED
        )


class DocumentPageOCRAPIViewSet(MayanAPIGenericViewSet):
    lookup_url_kwarg = 'document_page_id'
    object_permission_map = {
        'ocr_content': permission_ocr_content_view,
    }
    serializer_class = DocumentPageOCRContentSerializer

    def get_queryset(self):
        return get_object_or_404(
            klass=DocumentVersion, document_id=self.kwargs['document_id'],
            pk=self.kwargs['document_version_id']
        ).pages.all()

    @action(
        detail=True, url_name='content', url_path='ocr'
    )
    def ocr_content(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(data=serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )


class DocumentVersionOCRAPIViewSet(MayanAPIViewSet):
    lookup_url_kwarg = 'document_version_id'
    object_permission_map = {
        'ocr_content': permission_ocr_content_view,
        'ocr_submit': permission_ocr_document,
    }
    queryset = DocumentVersion.objects.all()
    serializer_class = DocumentVersionOCRSerializer

    @action(
        detail=True, url_name='content', url_path='ocr'
    )
    def ocr_content(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(data=serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    @action(
        detail=True, methods=('post',), url_name='submit',
        url_path='ocr/submit'
    )
    def ocr_submit(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.submit_for_ocr(_user=request.user)
        return Response(
            data=None, status=status.HTTP_202_ACCEPTED
        )

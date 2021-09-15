from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .classes import Template
from .serializers import ContentTypeSerializer, TemplateSerializer


class ContentTypeAPIViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Return a list of all the available content types.

    retrieve:
    Return the given content type details.
    """
    lookup_url_kwarg = 'content_type_id'
    queryset = ContentType.objects.order_by('app_label', 'model')
    serializer_class = ContentTypeSerializer


class TemplateAPIViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Return a list of partial templates.

    retrieve:
    Return the given partial template details.
    """
    lookup_url_kwarg = 'template_name'
    permission_classes = (IsAuthenticated,)
    serializer_class = TemplateSerializer

    def get_object(self):
        return Template.get(name=self.kwargs['template_name']).render(
            request=self.request
        )

    def get_queryset(self):
        return Template.all(rendered=True, request=self.request)

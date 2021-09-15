from __future__ import absolute_import, unicode_literals

import logging

from furl import furl

from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView

from mayan.apps.common.generics import SimpleView, SingleObjectListView
from mayan.apps.common.mixins import ExternalObjectMixin
from mayan.apps.common.settings import setting_home_view
from mayan.apps.common.utils import resolve
from mayan.apps.converter.literals import DEFAULT_ROTATION, DEFAULT_ZOOM_LEVEL

from ..forms import DocumentPageForm
from ..models import Document, DocumentPage
from ..permissions import permission_document_view
from ..settings import (
    setting_rotation_step, setting_zoom_max_level, setting_zoom_min_level,
    setting_zoom_percent_step
)

__all__ = (
    'DocumentPageListView', 'DocumentPageNavigationFirst',
    'DocumentPageNavigationLast', 'DocumentPageNavigationNext',
    'DocumentPageNavigationPrevious', 'DocumentPageRotateLeftView',
    'DocumentPageRotateRightView', 'DocumentPageView',
    'DocumentPageViewResetView', 'DocumentPageZoomInView',
    'DocumentPageZoomOutView',
)
logger = logging.getLogger(__name__)


class DocumentPageInteractiveTransformation(ExternalObjectMixin, RedirectView):
    external_object_class = DocumentPage
    external_object_permission = permission_document_view
    external_object_pk_url_kwarg = 'document_page_id'

    def get_object(self):
        return self.get_external_object()

    def get_redirect_url(self, *args, **kwargs):
        query_dict = {
            'rotation': self.request.GET.get('rotation', DEFAULT_ROTATION),
            'zoom': self.request.GET.get('zoom', DEFAULT_ZOOM_LEVEL)
        }

        url = furl(
            args=query_dict, path=reverse(
                viewname='documents:document_page_view',
                kwargs={'document_page_id': self.kwargs['document_page_id']}
            )

        )

        self.transformation_function(query_dict=query_dict)

        return url.tostr()


class DocumentPageListView(ExternalObjectMixin, SingleObjectListView):
    external_object_class = Document
    external_object_permission = permission_document_view
    external_object_pk_url_kwarg = 'document_id'

    def get_document(self):
        return self.get_external_object()

    def get_extra_context(self):
        return {
            'column_class': 'col-xs-12 col-sm-6 col-md-4 col-lg-3',
            'hide_object': True,
            'list_as_items': True,
            'object': self.get_document(),
            'table_cell_container_classes': 'td-container-thumbnail',
            'title': _('Pages for document: %s') % self.get_document(),
        }

    def get_source_queryset(self):
        return self.get_document().pages.all()


class DocumentPageNavigationBase(ExternalObjectMixin, RedirectView):
    external_object_class = DocumentPage
    external_object_permission = permission_document_view
    external_object_pk_url_kwarg = 'document_page_id'

    def get_object(self):
        return self.get_external_object()

    def get_redirect_url(self, *args, **kwargs):
        """
        Attempt to jump to the same kind of view but resolved to a new
        object of the same kind.
        """
        previous_url = self.request.META.get('HTTP_REFERER', None)

        if not previous_url:
            try:
                previous_url = self.get_object().get_absolute_url()
            except AttributeError:
                previous_url = reverse(viewname=setting_home_view.value)

        parsed_url = furl(url=previous_url)

        # Obtain the view name to be able to resolve it back with new keyword
        # arguments.
        resolver_match = resolve(path=force_text(parsed_url.path))

        new_kwargs = self.get_new_kwargs()

        if set(new_kwargs) == set(resolver_match.kwargs):
            # It is the same type of object, reuse the URL to stay in the
            # same kind of view but pointing to a new object
            url = reverse(
                viewname=resolver_match.view_name, kwargs=new_kwargs
            )
        else:
            url = parsed_url.path

        # Update just the path to retain the querystring in case there is
        # transformation data.
        parsed_url.path = url

        return parsed_url.tostr()


class DocumentPageNavigationFirst(DocumentPageNavigationBase):
    def get_new_kwargs(self):
        document_page = self.get_object()

        return {'document_page_id': document_page.siblings.first().pk}


class DocumentPageNavigationLast(DocumentPageNavigationBase):
    def get_new_kwargs(self):
        document_page = self.get_object()

        return {'document_page_id': document_page.siblings.last().pk}


class DocumentPageNavigationNext(DocumentPageNavigationBase):
    def get_new_kwargs(self):
        document_page = self.get_object()

        try:
            document_page = document_page.siblings.get(
                page_number=document_page.page_number + 1
            )
        except DocumentPage.DoesNotExist:
            messages.warning(
                message=_(
                    'There are no more pages in this document'
                ), request=self.request
            )
        finally:
            return {'document_page_id': document_page.pk}


class DocumentPageNavigationPrevious(DocumentPageNavigationBase):
    def get_new_kwargs(self):
        document_page = self.get_object()

        try:
            document_page = document_page.siblings.get(
                page_number=document_page.page_number - 1
            )
        except DocumentPage.DoesNotExist:
            messages.warning(
                message=_(
                    'You are already at the first page of this document'
                ), request=self.request
            )
        finally:
            return {'document_page_id': document_page.pk}


class DocumentPageRotateLeftView(DocumentPageInteractiveTransformation):
    def transformation_function(self, query_dict):
        query_dict['rotation'] = (
            int(query_dict['rotation']) - setting_rotation_step.value
        ) % 360


class DocumentPageRotateRightView(DocumentPageInteractiveTransformation):
    def transformation_function(self, query_dict):
        query_dict['rotation'] = (
            int(query_dict['rotation']) + setting_rotation_step.value
        ) % 360


class DocumentPageView(ExternalObjectMixin, SimpleView):
    external_object_class = DocumentPage
    external_object_permission = permission_document_view
    external_object_pk_url_kwarg = 'document_page_id'
    template_name = 'appearance/generic_form.html'

    def get_extra_context(self):
        zoom = int(self.request.GET.get('zoom', DEFAULT_ZOOM_LEVEL))
        rotation = int(self.request.GET.get('rotation', DEFAULT_ROTATION))

        document_page_form = DocumentPageForm(
            instance=self.get_object(), rotation=rotation, zoom=zoom
        )

        base_title = _('Image of: %s') % self.get_object()

        if zoom != DEFAULT_ZOOM_LEVEL:
            zoom_text = '({}%)'.format(zoom)
        else:
            zoom_text = ''

        return {
            'form': document_page_form,
            'hide_labels': True,
            'navigation_object_list': ('page',),
            'page': self.get_object(),
            'rotation': rotation,
            'title': ' '.join((base_title, zoom_text)),
            'read_only': True,
            'zoom': zoom,
        }

    def get_object(self):
        return self.get_external_object()


class DocumentPageViewResetView(RedirectView):
    pattern_name = 'documents:document_page_view'


class DocumentPageZoomInView(DocumentPageInteractiveTransformation):
    def transformation_function(self, query_dict):
        zoom = int(query_dict['zoom']) + setting_zoom_percent_step.value

        if zoom > setting_zoom_max_level.value:
            zoom = setting_zoom_max_level.value

        query_dict['zoom'] = zoom


class DocumentPageZoomOutView(DocumentPageInteractiveTransformation):
    def transformation_function(self, query_dict):
        zoom = int(query_dict['zoom']) - setting_zoom_percent_step.value

        if zoom < setting_zoom_min_level.value:
            zoom = setting_zoom_min_level.value

        query_dict['zoom'] = zoom

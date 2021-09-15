from __future__ import absolute_import, unicode_literals

import logging

from django.template import RequestContext
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.generics import (
    SingleObjectCreateView, SingleObjectDeleteView, SingleObjectEditView,
    SingleObjectListView
)
from mayan.apps.common.mixins import ContentTypeViewMixin, ExternalObjectMixin

from .forms import TransformationForm
from .icons import icon_transformation
from .links import link_transformation_create
from .models import Transformation
from .permissions import (
    permission_transformation_create, permission_transformation_delete,
    permission_transformation_edit, permission_transformation_view
)

logger = logging.getLogger(__name__)


class TransformationCreateView(ContentTypeViewMixin, ExternalObjectMixin, SingleObjectCreateView):
    external_object_permission = permission_transformation_create
    external_object_pk_url_kwarg = 'object_id'
    form_class = TransformationForm

    def get_external_object_queryset(self):
        return self.get_content_type().model_class().objects.all()

    def get_extra_context(self):
        return {
            'content_object': self.external_object,
            'navigation_object_list': ('content_object',),
            'title': _(
                'Create new transformation for: %s'
            ) % self.external_object,
        }

    def get_instance_extra_data(self):
        return {'content_object': self.external_object}

    def get_post_action_redirect(self):
        return reverse(
            viewname='converter:transformation_list', kwargs={
                'app_label': self.kwargs['app_label'],
                'model': self.kwargs['model'],
                'object_id': self.kwargs['object_id']
            }
        )

    def get_queryset(self):
        return Transformation.objects.get_for_model(obj=self.external_object)


class TransformationDeleteView(SingleObjectDeleteView):
    model = Transformation
    object_permission = permission_transformation_delete
    pk_url_kwarg = 'transformation_id'

    def get_extra_context(self):
        transformation = self.get_object()

        return {
            'content_object': transformation.content_object,
            'navigation_object_list': ('content_object', 'transformation'),
            'previous': reverse(
                viewname='converter:transformation_list', kwargs={
                    'app_label': transformation.content_type.app_label,
                    'model': transformation.content_type.model,
                    'object_id': transformation.object_id
                }
            ),
            'title': _(
                'Delete transformation "%(transformation)s" for: '
                '%(content_object)s?'
            ) % {
                'transformation': transformation,
                'content_object': transformation.content_object
            },
            'transformation': transformation,
        }

    def get_post_action_redirect(self):
        transformation = self.get_object()

        return reverse(
            viewname='converter:transformation_list', kwargs={
                'app_label': transformation.content_type.app_label,
                'model': transformation.content_type.model,
                'object_id': transformation.object_id
            }
        )


class TransformationEditView(SingleObjectEditView):
    form_class = TransformationForm
    model = Transformation
    object_permission = permission_transformation_edit
    pk_url_kwarg = 'transformation_id'

    def get_extra_context(self):
        transformation = self.get_object()

        return {
            'content_object': transformation.content_object,
            'navigation_object_list': ('content_object', 'transformation'),
            'title': _(
                'Edit transformation "%(transformation)s" for: %(content_object)s'
            ) % {
                'transformation': transformation,
                'content_object': transformation.content_object
            },
            'transformation': transformation,
        }

    def get_post_action_redirect(self):
        transformation = self.get_object()

        return reverse(
            viewname='converter:transformation_list', kwargs={
                'app_label': transformation.content_type.app_label,
                'model': transformation.content_type.model,
                'object_id': transformation.object_id
            }
        )


class TransformationListView(ContentTypeViewMixin, ExternalObjectMixin, SingleObjectListView):
    external_object_permission = permission_transformation_view
    external_object_pk_url_kwarg = 'object_id'

    def get_external_object_queryset(self):
        return self.get_content_type().model_class().objects.all()

    def get_extra_context(self):
        return {
            'content_object': self.external_object,
            'hide_link': True,
            'hide_object': True,
            'navigation_object_list': ('content_object',),
            'no_results_icon': icon_transformation,
            'no_results_main_link': link_transformation_create.resolve(
                context=RequestContext(
                    dict_={'content_object': self.external_object},
                    request=self.request
                )
            ),
            'no_results_text': _(
                'Transformations allow changing the visual appearance '
                'of documents without making permanent changes to the '
                'document file themselves.'
            ),
            'no_results_title': _('No transformations'),
            'title': _('Transformations for: %s') % self.external_object
        }

    def get_source_queryset(self):
        return Transformation.objects.get_for_model(obj=self.external_object)

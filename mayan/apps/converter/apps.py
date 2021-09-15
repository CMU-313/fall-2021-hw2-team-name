from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.common import MayanAppConfig, menu_object, menu_secondary
from mayan.apps.navigation import SourceColumn

from .links import (
    link_transformation_create, link_transformation_delete,
    link_transformation_edit
)
from .licenses import *  # NOQA


class ConverterApp(MayanAppConfig):
    app_namespace = 'converter'
    app_url = 'converter'
    has_tests = True
    name = 'mayan.apps.converter'
    verbose_name = _('Converter')

    def ready(self):
        super(ConverterApp, self).ready()

        Transformation = self.get_model(model_name='Transformation')

        ModelPermission.register_inheritance(
            model=Transformation, related='content_object'
        )

        SourceColumn(
            attribute='order', include_label=True, source=Transformation
        )
        SourceColumn(
            attribute='get_transformation_label', is_identifier=True,
            source=Transformation
        )
        SourceColumn(
            attribute='arguments', include_label=True, source=Transformation
        )

        menu_object.bind_links(
            links=(link_transformation_edit, link_transformation_delete),
            sources=(Transformation,)
        )
        menu_secondary.bind_links(
            links=(link_transformation_create,), sources=(Transformation,)
        )
        menu_secondary.bind_links(
            links=(link_transformation_create,),
            sources=(
                'converter:transformation_create',
                'converter:transformation_list'
            )
        )

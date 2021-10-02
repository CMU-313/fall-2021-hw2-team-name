from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.acls.permissions import permission_acl_edit, permission_acl_view
from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.classes import ModelCopy, ModelQueryFields

from mayan.apps.events.classes import EventModelRegistry, ModelEventType

from mayan.apps.navigation.classes import SourceColumn

from .events import (
    event_cabinet_edited, event_cabinet_document_added,
    event_cabinet_document_removed
)
from .html_widgets import DocumentCabinetWidget

from .menus import menu_cabinets
from .methods import method_document_get_cabinets


class ReviewerFormApp(MayanAppConfig):
    app_namespace = 'reviewer_form'
    app_url = 'reviewer_form'
    has_rest_api = True
    has_static_media = True
    has_tests = False
    name = 'mayan.apps.reviewer_form'

    verbose_name = _('reviewer_form')

    def ready(self):
        super().ready()

        ReviewerForm = self.get_model(model_name='ReviewerForm')
     
        EventModelRegistry.register(model=ReviewerForm)

        ModelCopy(
            model=ReviewerForm, 
            bind_link=True, register_permission=True
        ).add_fields(

            //YAJIN: to be modified
            field_names=('label', 'documents')
            }
        )

        ModelEventType.register(
            model=ReviewerForm, event_types=(
                reviewer_form_created
            )
        )

        # ModelPermission.register(
        #     model=Document, permissions=(
        #         permission_cabinet_add_document,
        #         permission_cabinet_remove_document, permission_cabinet_view,
        #         permission_events_view
        #     )
        # )

        # ModelPermission.register(
        #     model=Cabinet, permissions=(
        #         permission_acl_edit, permission_acl_view,
        #         permission_cabinet_delete, permission_cabinet_edit,
        #         permission_cabinet_view, permission_cabinet_add_document,
        #         permission_cabinet_remove_document
        #     )
        # )

  
        SourceColumn(
            attribute='label', is_identifier=True, is_sortable=True,
            source=Cabinet
        )

        SourceColumn(
            attribute='label', is_identifier=True, is_sortable=True,
            source=CabinetSearchResult
        )
        SourceColumn(
            attribute='get_full_path', source=CabinetSearchResult
        )

        SourceColumn(
            label=_('Cabinets'), order=1, source=Document,
            widget=DocumentCabinetWidget
        )


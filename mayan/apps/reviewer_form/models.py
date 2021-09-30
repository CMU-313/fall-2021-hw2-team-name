from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import connection, models, transaction
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mptt.fields import TreeForeignKey

from mayan.apps.acls.models import AccessControlList
from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.events.classes import EventManagerMethodAfter, EventManagerSave
from mayan.apps.events.decorators import method_event

from .events import (
    event_cabinet_created, event_cabinet_edited, event_cabinet_document_added,
    event_cabinet_document_removed
)


class ReviewerForm(ExtraDataModelMixin, models.Model):

    label = models.CharField(
        help_text= 'text for reviewer form',
        max_length=128, verbose_name=_('Label')
    )
    documents = models.ManyToManyField(
        related_name='reviewer_forms', to=Document,
        verbose_name=_('Documents')
    )

    class Meta:
        # unique_together doesn't work if there is a FK
        # https://code.djangoproject.com/ticket/1751
        ordering = ('label')
        verbose_name = _('ReviewerForm')
        verbose_name_plural = _('ReviewerForms')

    def __str__(self):
        return self.label



    def get_absolute_url(self):
        return reverse(
            viewname='cabinets:cabinet_view', kwargs={
                'cabinet_id': self.pk
            }
        )

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_reviewer_form_created,
            'target': 'self',
        },
        edited={
            'event': event_reviewer_form_edited,
            'target': 'self',
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class CabinetSearchResult(Cabinet):
    """
    Represent a cabinet's search result. This model is a proxy model from
    Cabinet and is used as an alias to map columns to it without having to
    map them to the base Cabinet model.
    """
    class Meta:
        proxy = True
        verbose_name = _('Cabinet')
        verbose_name_plural = _('Cabinets')


class DocumentCabinet(Cabinet):
    """
    Represent a document's cabinet. This Model is a proxy model from Cabinet
    and is used as an alias to map columns to it without having to map them
    to the base Cabinet model.
    """
    class Meta:
        proxy = True
        verbose_name = _('Document cabinet')
        verbose_name_plural = _('Document cabinets')

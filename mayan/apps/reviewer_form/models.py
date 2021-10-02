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


class ReviewerForm(models.Model):
    #TODO need to fill in more fields.

        
    first_name = forms.CharField(max_length=25, required=True)
    last_name = forms.CharField(max_length=25, required=True)
    email = forms.EmailField(max_length=50, label="Email Address", required=True)
    
    experience_score = forms.ChoiceField(choices=experience_score_choices, label="Experience Score:", required=True)
    skills_score = forms.ChoiceField(choices=skills_score_choices, label="Skill Score:", required=True)
    gpa_score = forms.ChoiceField(choices=gpa_score_choices, label="GPA Score:", required=True)
    essay_score = forms.ChoiceField(choices=essay_score_choices, label="Essay Score:", required=True)

    additional_comments = forms.CharField(widget=forms.Textarea, label="Additional Comments:", required=True)
    reviewer_name = forms.CharField(max_length=50, label="Reviewer Name", required=True)

    final_decision = forms.ChoiceField(choices=final_decision_choices, label="Final Decision:", required=True)


    class Meta:
        # unique_together doesn't work if there is a FK
        # https://code.djangoproject.com/ticket/1751
        ordering = ('first_name')
        verbose_name = _('ReviewerForm')
        verbose_name_plural = _('ReviewerForms')

    def __str__(self):
        return self.label


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


from django.utils.translation import ugettext_lazy as _

from mayan.apps.events.classes import EventTypeNamespace

namespace = EventTypeNamespace(label=_('ReviewerForms'), name='reviewerForm')


event_cabinet_created = namespace.add_event_type(
    label=_('Reviewer Form created'), name='reviewer_form_created'
)

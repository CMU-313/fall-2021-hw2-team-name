from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.forms import DetailForm

from .models import Key


class KeyDetailForm(DetailForm):
    class Meta:
        extra_fields = (
            {'field': 'key_id'},
            {'field': 'get_escaped_user_id'},
            {'field': 'creation_date', 'widget': forms.widgets.DateInput},
            {
                'field': 'get_expiration_date_display',
                'widget': forms.widgets.DateInput
            },
            {'field': 'fingerprint'},
            {'field': 'length'},
            {'field': 'algorithm'},
            {'label': _('Type'), 'field': 'get_key_type_display'},
        )
        fields = ()
        model = Key


class KeySearchForm(forms.Form):
    term = forms.CharField(
        help_text=_('Name, e-mail, key ID or key fingerprint to look for.'),
        label=_('Term')
    )

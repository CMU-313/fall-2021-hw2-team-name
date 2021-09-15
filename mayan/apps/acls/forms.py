from __future__ import unicode_literals

from django import forms

from mayan.apps.common.forms import FilteredSelectionForm

from .models import AccessControlList


class ACLCreateForm(FilteredSelectionForm, forms.ModelForm):
    class Meta:
        fields = ('role',)
        model = AccessControlList

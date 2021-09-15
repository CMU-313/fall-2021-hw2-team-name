from __future__ import absolute_import, unicode_literals

import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from ..fields import DocumentPageField

__all__ = ('DocumentPageForm', 'DocumentPageNumberForm')
logger = logging.getLogger(__name__)


class DocumentPageForm(forms.Form):
    document_page = DocumentPageField()

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        rotation = kwargs.pop('rotation', None)
        zoom = kwargs.pop('zoom', None)
        super(DocumentPageForm, self).__init__(*args, **kwargs)
        self.fields['document_page'].initial = instance
        self.fields['document_page'].widget.attrs.update({
            'zoom': zoom,
            'rotation': rotation,
        })


class DocumentPageNumberForm(forms.Form):
    page = forms.ModelChoiceField(
        help_text=_(
            'Page number from which all the transformation will be cloned. '
            'Existing transformations will be lost.'
        ), queryset=None
    )

    def __init__(self, *args, **kwargs):
        self.document = kwargs.pop('document')
        super(DocumentPageNumberForm, self).__init__(*args, **kwargs)
        self.fields['page'].queryset = self.document.pages.all()

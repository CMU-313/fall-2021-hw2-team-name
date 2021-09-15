from __future__ import absolute_import, unicode_literals

from django import forms

from .widgets import DocumentPageImageWidget, DocumentPagesCarouselWidget


class DocumentField(forms.fields.Field):
    widget = DocumentPagesCarouselWidget


class DocumentPageField(forms.fields.Field):
    widget = DocumentPageImageWidget


class DocumentVersionField(forms.fields.Field):
    widget = DocumentPagesCarouselWidget

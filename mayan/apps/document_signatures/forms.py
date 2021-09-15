from __future__ import absolute_import, unicode_literals

import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.forms import DetailForm, FilteredSelectionForm
from mayan.apps.django_gpg.models import Key
from mayan.apps.django_gpg.permissions import permission_key_sign

from .models import SignatureBaseModel

logger = logging.getLogger(__name__)


class DocumentVersionSignatureCreateForm(FilteredSelectionForm):
    key = forms.ModelChoiceField(
        label=_('Key'), queryset=Key.objects.none()
    )

    passphrase = forms.CharField(
        help_text=_(
            'The passphrase to unlock the key and allow it to be used to '
            'sign the document version.'
        ), label=_('Passphrase'), required=False,
        widget=forms.widgets.PasswordInput
    )

    class Meta:
        allow_multiple = False
        field_name = 'key'
        label = _('Key')
        help_text = _(
            'Private key that will be used to sign this document version.'
        )
        permission = permission_key_sign
        queryset = Key.objects.private_keys()
        required = True
        widget_attributes = {'class': 'select2'}


class DocumentVersionSignatureDetailForm(DetailForm):
    def __init__(self, *args, **kwargs):
        super(
            DocumentVersionSignatureDetailForm, self
        ).__init__(*args, **kwargs)

        extra_fields = self.Meta.extra_fields

        if kwargs['instance'].public_key_fingerprint:
            key = Key.objects.get(
                fingerprint=kwargs['instance'].public_key_fingerprint
            )

            extra_fields += (
                {'field': 'signature_id'},
                {
                    'field': 'fingerprint',
                    'object': key
                },
                {
                    'field': 'creation_date',
                    'object': key,
                    'widget': forms.widgets.DateInput
                },
                {
                    'field': 'get_expiration_date_display',
                    'object': key,
                    'widget': forms.widgets.DateInput
                },
                {
                    'field': 'length',
                    'object': key
                },
                {
                    'field': 'algorithm',
                    'object': key
                },
                {
                    'field': 'get_escaped_user_id',
                    'object': key
                },
                {
                    'field': 'get_key_type_display',
                    'object': key
                },
            )

        self.Meta.extra_fields = extra_fields

    class Meta:
        extra_fields = (
            {'field': 'get_signature_type_display'},
            {
                'field': 'date',
                'widget': forms.widgets.DateInput
            },
            {'field': 'key_id'},
            {
                'field': 'get_key_available_display'
            },
        )
        fields = ()
        model = SignatureBaseModel

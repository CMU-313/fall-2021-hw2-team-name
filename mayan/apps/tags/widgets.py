from __future__ import absolute_import, unicode_literals

from django import forms
from django.utils.html import conditional_escape


class TagFormWidget(forms.SelectMultiple):
    option_template_name = 'tags/forms/widgets/tag_select_option.html'

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')
        return super(TagFormWidget, self).__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        result = super(TagFormWidget, self).create_option(
            attrs=attrs, index=index,
            label='{}'.format(conditional_escape(label)), name=name,
            selected=selected, subindex=subindex, value=value
        )

        result['attrs']['data-color'] = self.queryset.get(pk=value).color

        return result

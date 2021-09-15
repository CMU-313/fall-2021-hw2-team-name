from __future__ import unicode_literals

from django import forms
from django.template import Context, Template
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from .icons import icon_fail as default_icon_fail
from .icons import icon_ok as default_icon_ok


class ButtonWidget(forms.widgets.Widget):
    template_name = 'common/forms/widgets/button_widget.html'

    def format_value(self, value):
        if value == '' or value is None:
            return None
        return value


class DisableableSelectWidget(forms.widgets.SelectMultiple):
    def create_option(self, *args, **kwargs):
        result = super(DisableableSelectWidget, self).create_option(*args, **kwargs)

        # Get a keyword argument named value or the second positional argument
        # Current interface as of Django 1.11
        # def create_option(self, name, value, label, selected, index,
        # subindex=None, attrs=None):
        value = kwargs.get('value', args[1])

        if value in self.disabled_choices:
            result['attrs'].update({'disabled': 'disabled'})

        return result


# From: http://www.peterbe.com/plog/emailinput-html5-django
class EmailInput(forms.widgets.Input):
    """
    Class for a login form widget that accepts only well formated
    email address
    """
    input_type = 'email'

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update(
            {
                'autocorrect': 'off', 'autocapitalize': 'off',
                'spellcheck': 'false'
            }
        )
        return super(EmailInput, self).render(name, value, attrs=attrs)


class ObjectLinkWidget(object):
    template_string = '<a href="{{ url }}">{{ object_type }}{{ label }}</a>'

    def __init__(self):
        self.template = Template(template_string=self.template_string)

    def render(self, name=None, value=None):
        label = ''
        object_type = ''
        url = None

        if value:
            label = force_text(value)
            object_type = '{}: '.format(value._meta.verbose_name)
            try:
                url = value.get_absolute_url()
            except AttributeError:
                url = None

        return self.template.render(
            context=Context(
                {'label': label, 'object_type': object_type, 'url': url or '#'}
            )
        )


class PlainWidget(forms.widgets.Widget):
    """
    Class to define a form widget that effectively nulls the htmls of a
    widget and reduces the output to only it's value
    """
    def render(self, name, value, attrs=None):
        return mark_safe('%s' % value)


class TextAreaDiv(forms.widgets.Widget):
    """
    Class to define a form widget that simulates the behavior of a
    Textarea widget but using a div tag instead
    """
    template_name = 'appearance/forms/widgets/textareadiv.html'

    def __init__(self, attrs=None):
        # The 'rows' and 'cols' attributes are required for HTML correctness.
        default_attrs = {'class': 'text_area_div'}
        if attrs:
            default_attrs.update(attrs)
        super(TextAreaDiv, self).__init__(default_attrs)


class TwoStateWidget(object):
    def __init__(self, center=False, icon_ok=None, icon_fail=None):
        self.icon_ok = icon_ok or default_icon_ok
        self.icon_fail = icon_fail or default_icon_fail
        self.center = center

    def render(self, name=None, value=None):
        center_class = ''
        if self.center:
            center_class = 'text-center'

        if value:
            return mark_safe(
                '<div class="{} text-success">{}</div>'.format(
                    center_class, self.icon_ok.render()
                )
            )
        else:
            return mark_safe(
                '<div class="{} text-danger">{}</div>'.format(
                    center_class, self.icon_fail.render()
                )
            )

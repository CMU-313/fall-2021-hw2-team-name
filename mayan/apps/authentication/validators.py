from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class MinimumCapitalLettersContentValidator(object):
    """
    Validate whether the password contains a minimum number of uppercase
    letters.
    """
    def __init__(self, minimum_capital_letters=1):
        self.minimum_capital_letters = minimum_capital_letters

    def validate(self, password, user=None):
        if sum([1 for letter in password if letter.isupper()]) < self.minimum_capital_letters:  # NOQA
            raise ValidationError(
                _(
                    'This password must contain at least '
                    '%(minimum_capital_letters)d capital letters.'
                ), code='password_not_enough_capital_letters',
                params={
                    'minimum_capital_letters': self.minimum_capital_letters
                },
            )

    def get_help_text(self):
        return _(
            'Your password must contain at least %(minimum_capital_letters)d '
            'capital letters.'
            % {'minimum_capital_letters': self.minimum_capital_letters}
        )


class MinimumNumberContentValidator(object):
    """
    Validate whether the password contains a minimum number digits.
    """
    def __init__(self, minimum_numbers=1):
        self.minimum_numbers = minimum_numbers

    def validate(self, password, user=None):
        if sum([1 for letter in password if letter.isdigit()]) < self.minimum_numbers:  # NOQA
            raise ValidationError(
                _(
                    'This password must contain at least %(minimum_numbers)d '
                    'numbers.'
                ), code='password_not_enough_numbers',
                params={'minimum_numbers': self.minimum_numbers},
            )

    def get_help_text(self):
        return _(
            'Your password must contain at least %(minimum_numbers)d numbers.'
            % {'minimum_numbers': self.minimum_numbers}
        )

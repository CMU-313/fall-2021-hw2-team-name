*******************
Password validation
*******************

To help reduce the use of weak passwords, Mayan EDMS includes support for
password validators. Password validator enforce policies by rejecting
password that don't conform with the validator's logic.

By default, Mayan EDMS sets this password validation setup:

- That the password is not similar no any user attributes.
- A minimum password size of 8 characters.
- The password is not one of the 20,000 commonly used weak password.
- That the password is not entirely numeric.

This default is coded in the following manner by the default Python setup file::

    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

If using the YAML configuration file the same setup would be coded in the
following manner::

    AUTH_PASSWORD_VALIDATORS:
    - NAME: django.contrib.auth.password_validation.UserAttributeSimilarityValidator
    - NAME: django.contrib.auth.password_validation.MinimumLengthValidator
    - NAME: django.contrib.auth.password_validation.CommonPasswordValidator
    - NAME: django.contrib.auth.password_validation.NumericPasswordValidator

In addition to the password validators provided by Django
:django-docs:`validators provided by Django <topics/auth/passwords/#included-validators>`,
Mayan EDMS adds the following validators:

.. autoclass:: mayan.apps.authentication.validators.MinimumCapitalLettersContentValidator

.. autoclass:: mayan.apps.authentication.validators.MinimumNumberContentValidator

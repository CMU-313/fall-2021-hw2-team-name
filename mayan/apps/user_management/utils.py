from __future__ import unicode_literals

from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _


def get_groups():
    Group = apps.get_model(app_label='auth', model_name='Group')
    return ','.join([group.name for group in Group.objects.all()])


def get_users():
    return ','.join(
        [
            user.get_full_name() or user.username
            for user in get_user_model().objects.all()
        ]
    )


def get_user_label_text(context):
    if not context['request'].user.is_authenticated:
        return _('Anonymous')
    else:
        return context['request'].user.get_full_name() or context['request'].user

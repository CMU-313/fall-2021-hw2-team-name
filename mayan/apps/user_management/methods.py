from __future__ import unicode_literals

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import reverse

from .events import (
    event_group_created, event_group_edited, event_user_created,
    event_user_edited
)
from .permissions import permission_group_view, permission_user_view
from .querysets import get_user_queryset


def method_group_get_users(self, _user):
    AccessControlList = apps.get_model(
        app_label='acls', model_name='AccessControlList'
    )

    return AccessControlList.objects.restrict_queryset(
        permission=permission_user_view, queryset=get_user_queryset(),
        user=_user
    )


def get_method_group_save():
    Group = apps.get_model(app_label='auth', model_name='Group')
    group_save_original = Group.save

    def method_group_save(self, *args, **kwargs):
        _user = kwargs.pop('_user', None)

        with transaction.atomic():
            is_new = not self.pk
            group_save_original(self, *args, **kwargs)
            if is_new:
                event_group_created.commit(
                    actor=_user, target=self
                )
            else:
                event_group_edited.commit(
                    actor=_user, target=self
                )

    return method_group_save


def method_group_users_add(self, users, _user):
    with transaction.atomic():
        event_group_edited.commit(
            actor=_user, target=self
        )
        for user in users:
            self.user_set.add(user)
            event_user_edited.commit(
                actor=_user, target=user
            )


def method_group_users_remove(self, users, _user):
    with transaction.atomic():
        event_group_edited.commit(
            actor=_user, target=self
        )
        for user in users:
            self.user_set.remove(user)
            event_user_edited.commit(
                actor=_user, target=user
            )


def method_user_get_absolute_url(self):
    return reverse(
        viewname='user_management:user_details', kwargs={'user_id': self.pk}
    )


def method_user_get_groups(self, _user):
    AccessControlList = apps.get_model(
        app_label='acls', model_name='AccessControlList'
    )

    return AccessControlList.objects.restrict_queryset(
        permission=permission_group_view, queryset=self.groups.all(),
        user=_user
    )


def method_user_groups_add(self, groups, _user):
    with transaction.atomic():
        event_user_edited.commit(
            actor=_user, target=self
        )
        for group in groups:
            self.groups.add(group)
            event_group_edited.commit(
                actor=_user, target=group
            )


def method_user_groups_remove(self, groups, _user):
    with transaction.atomic():
        event_user_edited.commit(
            actor=_user, target=self
        )
        for group in groups:
            self.groups.remove(group)
            event_group_edited.commit(
                actor=_user, target=group
            )


def get_method_user_save():
    user_save_original = get_user_model().save

    def method_user_save(self, *args, **kwargs):
        _user = kwargs.pop('_user', None)

        with transaction.atomic():
            is_new = not self.pk
            user_save_original(self, *args, **kwargs)
            if is_new:
                event_user_created.commit(
                    actor=_user, target=self
                )
            else:
                event_user_edited.commit(
                    actor=_user, target=self
                )

    return method_user_save

from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.urls import reverse, reverse_lazy
from django.utils.translation import ungettext, ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.generics import (
    AssignRemoveView, MultipleObjectConfirmActionView,
    MultipleObjectFormActionView, SingleObjectCreateView,
    SingleObjectDeleteView, SingleObjectDetailView, SingleObjectEditView,
    SingleObjectListView
)
from mayan.apps.common.mixins import ExternalObjectMixin

from .forms import UserForm
from .icons import icon_group_setup, icon_user_setup
from .links import link_group_create, link_user_create
from .permissions import (
    permission_group_create, permission_group_delete, permission_group_edit,
    permission_group_view, permission_user_create, permission_user_delete,
    permission_user_edit, permission_user_view
)


class CurrentUserDetailsView(SingleObjectDetailView):
    fields = (
        'username', 'first_name', 'last_name', 'email', 'last_login',
        'date_joined', 'groups'
    )

    def get_object(self):
        return self.request.user

    def get_extra_context(self, **kwargs):
        return {
            'object': None,
            'title': _('Current user details'),
        }


class CurrentUserEditView(SingleObjectEditView):
    extra_context = {'object': None, 'title': _('Edit current user details')}
    form_class = UserForm
    post_action_redirect = reverse_lazy(
        viewname='user_management:current_user_details'
    )

    def get_object(self):
        return self.request.user


class GroupCreateView(SingleObjectCreateView):
    extra_context = {'title': _('Create new group')}
    fields = ('name',)
    model = Group
    post_action_redirect = reverse_lazy(viewname='user_management:group_list')
    view_permission = permission_group_create


class GroupDeleteView(SingleObjectDeleteView):
    model = Group
    object_permission = permission_group_delete
    pk_url_kwarg = 'group_id'
    post_action_redirect = reverse_lazy(viewname='user_management:group_list')

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Delete the group: %s?') % self.object,
        }


class GroupEditView(SingleObjectEditView):
    fields = ('name',)
    model = Group
    object_permission = permission_group_edit
    pk_url_kwarg = 'group_id'
    post_action_redirect = reverse_lazy(viewname='user_management:group_list')

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Edit group: %s') % self.object,
        }


class GroupListView(SingleObjectListView):
    model = Group
    object_permission = permission_group_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_group_setup,
            'no_results_main_link': link_group_create.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'User groups are organizational units. They should '
                'mirror the organizational units of your organization. '
                'Groups can\'t be used for access control. Use roles '
                'for permissions and access control, add groups to '
                'them.'
            ),
            'no_results_title': _('There are no user groups'),
            'title': _('Groups'),
        }


class GroupMembersView(ExternalObjectMixin, AssignRemoveView):
    decode_content_type = True
    external_object_class = Group
    external_object_permission = permission_group_edit
    external_object_pk_url_kwarg = 'group_id'
    left_list_title = _('Available users')
    object_permission = permission_group_edit
    right_list_title = _('Users in group')

    @staticmethod
    def generate_choices(choices):
        results = []
        for choice in choices:
            ct = ContentType.objects.get_for_model(model=choice)
            label = choice.get_full_name() if choice.get_full_name() else choice

            results.append(('%s,%s' % (ct.model, choice.pk), '%s' % (label)))

        # Sort results by the label not the key value
        return sorted(results, key=lambda x: x[1])

    def add(self, item):
        self.object.user_set.add(item)

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        return super(GroupMembersView, self).dispatch(*args, **kwargs)

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Users of group: %s') % self.object
        }

    def get_object(self):
        return self.get_external_object()

    def left_list(self):
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_user_edit,
            queryset=get_user_model().objects.exclude(
                groups=self.object
            ).exclude(is_staff=True).exclude(is_superuser=True),
            user=self.request.user
        )

        return GroupMembersView.generate_choices(choices=queryset)

    def right_list(self):
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_user_edit,
            queryset=self.object.user_set.all(),
            user=self.request.user
        )

        return GroupMembersView.generate_choices(choices=queryset)

    def remove(self, item):
        self.object.user_set.remove(item)


class UserCreateView(SingleObjectCreateView):
    extra_context = {
        'title': _('Create new user'),
    }
    form_class = UserForm
    view_permission = permission_user_create

    def form_valid(self, form):
        super(UserCreateView, self).form_valid(form=form)
        return HttpResponseRedirect(
            reverse(
                viewname='user_management:user_set_password',
                kwargs={'user_id': self.object.pk}
            )
        )


class UserDeleteView(MultipleObjectConfirmActionView):
    object_permission = permission_user_delete
    pk_url_kwarg = 'user_id'
    source_queryset = get_user_model().objects.filter(
        is_superuser=False, is_staff=False
    )
    success_message_singular = _('User delete request performed on %(count)d user')
    success_message_plural = _(
        'User delete request performed on %(count)d users'
    )

    def get_extra_context(self):
        queryset = self.get_object_list()

        result = {
            'title': ungettext(
                singular='Delete user',
                plural='Delete users',
                number=queryset.count()
            )
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _('Delete user: %s') % queryset.first()
                }
            )

        return result

    def object_action(self, form, instance):
        try:
            instance.delete()
            messages.success(
                message=_(
                    'User "%s" deleted successfully.'
                ) % instance, request=self.request
            )
        except Exception as exception:
            messages.error(
                message=_(
                    'Error deleting user "%(user)s": %(error)s'
                ) % {'user': instance, 'error': exception},
                request=self.request
            )


class UserDetailsView(SingleObjectDetailView):
    fields = (
        'username', 'first_name', 'last_name', 'email', 'last_login',
        'date_joined', 'groups',
    )
    object_permission = permission_user_view
    pk_url_kwarg = 'user_id'
    source_queryset = get_user_model().objects.filter(
        is_superuser=False, is_staff=False
    )

    def get_extra_context(self, **kwargs):
        return {
            'object': self.get_object(),
            'title': _('Details of user: %s') % self.get_object()
        }


class UserEditView(SingleObjectEditView):
    fields = ('username', 'first_name', 'last_name', 'email', 'is_active',)
    object_permission = permission_user_edit
    pk_url_kwarg = 'user_id'
    post_action_redirect = reverse_lazy(viewname='user_management:user_list')
    source_queryset = get_user_model().objects.filter(
        is_superuser=False, is_staff=False
    )

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Edit user: %s') % self.object,
        }


class UserGroupsView(ExternalObjectMixin, AssignRemoveView):
    decode_content_type = True
    external_object_queryset = get_user_model().objects.filter(
        is_staff=False, is_superuser=False
    )
    external_object_permission = permission_user_edit
    external_object_pk_url_kwarg = 'user_id'
    left_list_title = _('Available groups')
    right_list_title = _('Groups joined')

    def add(self, item):
        item.user_set.add(self.external_object)

    def get_extra_context(self):
        return {
            'object': self.external_object,
            'title': _('Groups of user: %s') % self.external_object
        }

    def get_object(self):
        return self.get_external_object()

    def left_list(self):
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_group_edit,
            queryset=Group.objects.exclude(user=self.external_object),
            user=self.request.user
        )
        return AssignRemoveView.generate_choices(choices=queryset)

    def right_list(self):
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_group_edit,
            queryset=Group.objects.filter(user=self.external_object),
            user=self.request.user
        )
        return AssignRemoveView.generate_choices(choices=queryset)

    def remove(self, item):
        item.user_set.remove(self.external_object)


class UserListView(SingleObjectListView):
    object_permission = permission_user_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_user_setup,
            'no_results_main_link': link_user_create.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'User accounts can be create from this view. After creating '
                'an user account you will prompted to set a password for it. '
            ),
            'no_results_title': _('There are no user accounts'),
            'title': _('Users'),
        }

    def get_source_queryset(self):
        return get_user_model().objects.exclude(
            is_superuser=True
        ).exclude(is_staff=True).order_by('last_name', 'first_name')


class UserOptionsEditView(SingleObjectEditView):
    fields = ('block_password_change',)
    object_permission = permission_user_edit

    def get_extra_context(self):
        return {
            'object': self.get_user(),
            'title': _(
                'Edit options for user: %s'
            ) % self.get_user()
        }

    def get_object(self, queryset=None):
        return self.get_user().user_options

    def get_post_action_redirect(self):
        return reverse(viewname='user_management:user_list')

    def get_user(self):
        return get_object_or_404(
            klass=get_user_model().objects.filter(
                is_superuser=False, is_staff=False
            ), pk=self.kwargs['user_id']
        )


class UserSetPasswordView(MultipleObjectFormActionView):
    form_class = SetPasswordForm
    model = get_user_model()
    object_permission = permission_user_edit
    pk_url_kwarg = 'user_id'
    source_queryset = get_user_model().objects.filter(
        is_superuser=False, is_staff=False
    )
    success_message_singular = _('Password change request performed on %(count)d user')
    success_message_plural = _(
        'Password change request performed on %(count)d users'
    )

    def get_extra_context(self):
        queryset = self.get_object_list()

        result = {
            'submit_label': _('Submit'),
            'title': ungettext(
                singular='Change the password of the %(count)d selected user',
                plural='Change the password of the %(count)d selected users',
                number=queryset.count()
            ) % {'count': queryset.count()}
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _(
                        'Change the password of user: %s'
                    ) % queryset.first()
                }
            )

        return result

    def get_form_extra_kwargs(self):
        queryset = self.get_object_list()
        return {'user': queryset.first()}

    def object_action(self, form, instance):
        try:
            instance.set_password(form.cleaned_data['new_password1'])
            instance.save()
            messages.success(
                message=_(
                    'Successful password reset for user: %s.'
                ) % instance, request=self.request
            )
        except Exception as exception:
            messages.error(
                message=_(
                    'Error reseting password for user "%(user)s": %(error)s'
                ) % {
                    'user': instance, 'error': exception
                }, request=self.request
            )

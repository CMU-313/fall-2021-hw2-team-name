from __future__ import absolute_import, unicode_literals

from django.core.exceptions import PermissionDenied

from rest_framework.permissions import BasePermission

from mayan.apps.permissions import Permission


class MayanViewSetPermission(BasePermission):
    def has_permission(self, request, view):
        """
        Block the API view by access using a permission.
        Required the view_permission_map class attribute which is a dictionary
        that matches a view actions ('create', 'destroy', etc) to a single
        permission instance.
        Example: view_permission_map = {
            'update': permission_..._edit
            'list': permission_..._view
        }
        """
        if not request.user or not request.user.is_authenticated:
            return False

        view_permission_dictionary = getattr(view, 'view_permission_map', {})
        view_permission = view_permission_dictionary.get(view.action, None)

        if view_permission:
            try:
                Permission.check_user_permission(
                    permission=view_permission, user=request.user
                )
            except PermissionDenied:
                return False
            else:
                return True
        else:
            return True

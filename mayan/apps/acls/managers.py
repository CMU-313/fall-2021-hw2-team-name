from __future__ import absolute_import, unicode_literals

import logging
import operator
import warnings

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import CharField, Value as V, Q
from django.db.models.functions import Concat
from django.http import Http404

from mayan.apps.common.utils import (
    get_related_field, resolve_attribute, return_related
)
from mayan.apps.common.warnings import InterfaceWarning
from mayan.apps.permissions import Permission
from mayan.apps.permissions.models import StoredPermission

from .classes import ModelPermission
from .exceptions import PermissionNotValidForClass

logger = logging.getLogger(__name__)


class AccessControlListManager(models.Manager):
    """
    Implement a 3 tier permission system, involving a permissions, an actor
    and an object
    """
    def _get_acl_filters(self, queryset, stored_permission, user, related_field_name=None):
        """
        This method does the bulk of the work. It generates filters for the
        AccessControlList model to determine if there are ACL entries for the
        members of the queryset's model provided.
        """
        # Determine which of the cases we need to address
        # 1: No related field
        # 2: Related field
        # 3: Related field that is Generic Foreign Key
        # 4: No related field, but has an inherited related field, solved by
        # recursion, branches to #2 or #3.
        # 5: Inherited field of a related field
        # -- Not addressed yet --
        # 6: Inherited field of a related field that is Generic Foreign Key
        result = []

        if related_field_name:
            related_field = get_related_field(
                model=queryset.model, related_field_name=related_field_name
            )

            if isinstance(related_field, GenericForeignKey):
                # Case 3: Generic Foreign Key, multiple ContentTypes + object
                # id combinations
                content_type_object_id_queryset = queryset.annotate(
                    ct_fk_combination=Concat(
                        related_field.ct_field, V('-'), related_field.fk_field,
                        output_field=CharField()
                    )
                ).values('ct_fk_combination')

                acl_filter = self.annotate(
                    ct_fk_combination=Concat(
                        'content_type', V('-'), 'object_id', output_field=CharField()
                    )
                ).filter(
                    permissions=stored_permission, role__groups__user=user,
                    ct_fk_combination__in=content_type_object_id_queryset
                ).values('object_id')

                field_lookup = 'object_id__in'

                result.append(Q(**{field_lookup: acl_filter}))
            else:
                # Case 2: Related field of a single type, single ContentType,
                # multiple object id
                content_type = ContentType.objects.get_for_model(
                    model=related_field.related_model
                )
                field_lookup = '{}_id__in'.format(related_field_name)
                acl_filter = self.filter(
                    content_type=content_type, permissions=stored_permission,
                    role__groups__user=user
                ).values('object_id')
                result.append(Q(**{field_lookup: acl_filter}))
                # Case 5: Related field, has an inherited related field itself
                # Bubble up permssion check
                # TODO: Add relationship support: OR or AND
                # TODO: OR for document pages, version, doc, and types
                # TODO: AND for new cabinet levels ACLs
                try:
                    related_field_model_related_fields = ModelPermission.get_inheritances(
                        model=related_field.related_model
                    )
                except KeyError:
                    pass
                else:
                    relation_result = []
                    for related_field_model_related_field_name in related_field_model_related_fields:
                        related_field_name = '{}__{}'.format(related_field_name, related_field_model_related_field_name)
                        related_field_inherited_acl_queries = self._get_acl_filters(
                            queryset=queryset, stored_permission=stored_permission,
                            user=user, related_field_name=related_field_name
                        )

                        relation_result.append(reduce(operator.and_, related_field_inherited_acl_queries))

                    result.append(reduce(operator.or_, relation_result))
        else:
            # Case 1: Original model, single ContentType, multiple object id
            content_type = ContentType.objects.get_for_model(model=queryset.model)
            field_lookup = 'id__in'
            acl_filter = self.filter(
                content_type=content_type, permissions=stored_permission,
                role__groups__user=user
            ).values('object_id')
            result.append(Q(**{field_lookup: acl_filter}))

            # Case 4: Original model, has an inherited related field
            try:
                related_fields = ModelPermission.get_inheritances(
                    model=queryset.model
                )
            except KeyError:
                pass
            else:
                relation_result = []

                for related_field_name in related_fields:
                    inherited_acl_queries = self._get_acl_filters(
                        queryset=queryset, stored_permission=stored_permission,
                        related_field_name=related_field_name, user=user
                    )
                    relation_result.append(reduce(operator.and_, inherited_acl_queries))

                result.append(reduce(operator.or_, relation_result))

        return result

    def check_access(self, obj, permission, user, raise_404=False):
        warnings.warn(
            'check_access() is deprecated, use restrict_queryset() to '
            'produce a queryset from which to .get() the corresponding '
            'object in the local code.', InterfaceWarning
        )
        queryset = self.restrict_queryset(
            permission=permission, queryset=obj._meta.default_manager.all(),
            user=user
        )

        if queryset.filter(pk=obj.pk).exists():
            return True
        else:
            if raise_404:
                raise Http404
            else:
                raise PermissionDenied

    def get_inherited_permissions(self, obj, role):
        queryset = self._get_inherited_object_permissions(obj=obj, role=role)

        queryset = queryset | role.permissions.all()

        # Filter the permissions to the ones that apply to the model
        queryset = ModelPermission.get_for_instance(
            instance=obj
        ).filter(
            pk__in=queryset
        )

        return queryset

    def _get_inherited_object_permissions(self, obj, role):
        queryset = StoredPermission.objects.none()

        if not obj:
            return queryset

        try:
            related_fields = ModelPermission.get_inheritances(
                model=type(obj)
            )
        except KeyError:
            pass
        else:
            for related_field_name in related_fields:
                try:
                    parent_object = resolve_attribute(
                        obj=obj, attribute=related_field_name
                    )
                except AttributeError:
                    # Parent accessor is not an attribute, try it as a related
                    # field.
                    parent_object = return_related(
                        instance=obj, related_field=related_field_name
                    )
                content_type = ContentType.objects.get_for_model(model=parent_object)
                try:
                    queryset = queryset | self.get(
                        content_type=content_type, object_id=parent_object.pk,
                        role=role
                    ).permissions.all()
                except self.model.DoesNotExist:
                    pass

                queryset = queryset | self._get_inherited_object_permissions(
                    obj=parent_object, role=role
                )

        return queryset

    def grant(self, obj, permission, role):
        class_permissions = ModelPermission.get_for_class(klass=obj.__class__)
        if permission not in class_permissions:
            raise PermissionNotValidForClass

        content_type = ContentType.objects.get_for_model(model=obj)
        acl, created = self.get_or_create(
            content_type=content_type, object_id=obj.pk,
            role=role
        )

        acl.permissions.add(permission.stored_permission)

        return acl

    def restrict_queryset_by_accesses(self, operator, permissions, queryset, user):
        result = []

        for permission in permissions:
            result.append(
                self.restrict_queryset(
                    permission=permission, queryset=queryset, user=user
                )
            )

        return reduce(operator, result)

    def restrict_queryset(self, permission, queryset, user):
        # Check directly granted permission via a role
        try:
            Permission.check_user_permission(permission=permission, user=user)
        except PermissionDenied:
            acl_filters = self._get_acl_filters(
                queryset=queryset,
                stored_permission=permission.stored_permission, user=user
            )

            final_query = None
            for acl_filter in acl_filters:
                if final_query is None:
                    final_query = acl_filter
                else:
                    final_query = final_query | acl_filter

            return queryset.filter(final_query)
        else:
            # User has direct permission assignment via a role, is superuser or
            # is staff. Return the entire queryset.
            return queryset

    def revoke(self, obj, permission, role):
        content_type = ContentType.objects.get_for_model(model=obj)
        acl, created = self.get_or_create(
            content_type=content_type, object_id=obj.pk,
            role=role
        )

        acl.permissions.remove(permission.stored_permission)

        if acl.permissions.count() == 0:
            acl.delete()

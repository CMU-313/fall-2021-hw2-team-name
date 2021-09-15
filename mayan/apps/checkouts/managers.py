from __future__ import absolute_import, unicode_literals

import logging

from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document

from .events import (
    event_document_auto_check_in, event_document_check_in,
    event_document_forceful_check_in
)
from .exceptions import DocumentNotCheckedOut, NewDocumentVersionNotAllowed
from .literals import STATE_CHECKED_IN, STATE_CHECKED_OUT
from .permissions import permission_document_check_in_override

logger = logging.getLogger(__name__)


class DocumentCheckoutManager(models.Manager):
    def check_in_document(self, document, user=None):
        try:
            document_checkout = self.model.objects.get(document=document)
        except self.model.DoesNotExist:
            raise DocumentNotCheckedOut(
                _('Document not checked out.')
            )
        else:
            with transaction.atomic():
                if user:
                    if self.get_document_checkout_info(document=document).user != user:
                        try:
                            AccessControlList.objects.check_access(
                                obj=document, permission=permission_document_check_in_override,
                                user=user
                            )
                        except PermissionDenied:
                            return
                        else:
                            event_document_forceful_check_in.commit(
                                actor=user, target=document
                            )
                    else:
                        event_document_check_in.commit(actor=user, target=document)
                else:
                    event_document_auto_check_in.commit(target=document)

                document_checkout.delete()

    def check_in_expired_check_outs(self):
        for document in self.get_expired_check_outs():
            document.check_in()

    def checkout_document(self, document, expiration_datetime, user, block_new_version=True):
        return self.create(
            block_new_version=block_new_version, document=document,
            expiration_datetime=expiration_datetime, user=user
        )

    def checked_out_documents(self):
        return Document.objects.filter(
            pk__in=self.model.objects.values('document__id')
        )

    def get_by_natural_key(self, document_natural_key):
        try:
            document = Document.objects.get_by_natural_key(document_natural_key)
        except Document.DoesNotExist:
            raise self.model.DoesNotExist

        return self.get(document__pk=document.pk)

    def get_document_checkout_info(self, document):
        try:
            return self.model.objects.get(document=document)
        except self.model.DoesNotExist:
            raise DocumentNotCheckedOut

    def get_document_checkout_state(self, document):
        if self.is_document_checked_out(document=document):
            return STATE_CHECKED_OUT
        else:
            return STATE_CHECKED_IN

    def get_expired_check_outs(self):
        expired_list = Document.objects.filter(
            pk__in=self.filter(
                expiration_datetime__lte=now()
            ).values('document__id')
        )
        logger.debug('expired_list: %s', expired_list)
        return expired_list

    def is_document_checked_out(self, document):
        return self.filter(document=document).exists()


class NewVersionBlockManager(models.Manager):
    def block(self, document):
        self.get_or_create(document=document)

    def get_by_natural_key(self, document_natural_key):
        try:
            document = Document.objects.get_by_natural_key(document_natural_key)
        except Document.DoesNotExist:
            raise self.model.DoesNotExist

        return self.get(document__pk=document.pk)

    def is_blocked(self, document):
        return self.filter(document=document).exists()

    def new_versions_allowed(self, document):
        if self.filter(document=document).exists():
            raise NewDocumentVersionNotAllowed

    def unblock(self, document):
        self.filter(document=document).delete()

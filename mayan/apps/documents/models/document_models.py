from __future__ import absolute_import, unicode_literals

import logging
import uuid

from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.db import models, transaction
from django.template import Context, Template
from django.urls import reverse
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList

from ..events import (
    event_document_create, event_document_properties_edit,
    event_document_type_change,
)
from ..managers import (
    DocumentManager, DuplicatedDocumentManager, FavoriteDocumentManager,
    PassthroughManager, RecentDocumentManager, TrashCanManager
)
from ..permissions import permission_document_view
from ..settings import setting_language
from ..signals import post_document_type_change

from .document_type_models import DocumentType

__all__ = (
    'Document', 'DuplicatedDocument', 'FavoriteDocument', 'RecentDocument',
    'TrashedDocument'
)
logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Document(models.Model):
    """
    Defines a single document with it's fields and properties
    Fields:
    * uuid - UUID of a document, universally Unique ID. An unique identifier
    generated for each document. No two documents can ever have the same UUID.
    This ID is generated automatically.
    """
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, help_text=_(
            'UUID of a document, universally Unique ID. An unique identifier '
            'generated for each document.'
        ), verbose_name=_('UUID')
    )
    document_type = models.ForeignKey(
        on_delete=models.CASCADE, related_name='documents', to=DocumentType,
        verbose_name=_('Document type')
    )
    label = models.CharField(
        blank=True, db_index=True, default='', max_length=255,
        help_text=_('The name of the document.'), verbose_name=_('Label')
    )
    description = models.TextField(
        blank=True, default='', help_text=_(
            'An optional short text describing a document.'
        ), verbose_name=_('Description')
    )
    date_added = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text=_(
            'The server date and time when the document was finally '
            'processed and added to the system.'
        ), verbose_name=_('Added')
    )
    language = models.CharField(
        blank=True, default=setting_language.value, help_text=_(
            'The dominant language in the document.'
        ), max_length=8, verbose_name=_('Language')
    )
    in_trash = models.BooleanField(
        db_index=True, default=False, help_text=_(
            'Whether or not this document is in the trash.'
        ), editable=False, verbose_name=_('In trash?')
    )
    deleted_date_time = models.DateTimeField(
        blank=True, editable=True, help_text=_(
            'The server date and time when the document was moved to the '
            'trash.'
        ), null=True, verbose_name=_('Date and time trashed')
    )
    is_stub = models.BooleanField(
        db_index=True, default=True, editable=False, help_text=_(
            'A document stub is a document with an entry on the database but '
            'no file uploaded. This could be an interrupted upload or a '
            'deferred upload via the API.'
        ), verbose_name=_('Is stub?')
    )

    objects = DocumentManager()
    passthrough = PassthroughManager()
    trash = TrashCanManager()

    class Meta:
        ordering = ('label',)
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')

    def __str__(self):
        return self.label or ugettext('Document stub, id: %d') % self.pk

    def add_as_recent_document_for_user(self, user):
        return RecentDocument.objects.add_document_for_user(user, self)

    def delete(self, *args, **kwargs):
        to_trash = kwargs.pop('to_trash', True)

        if not self.in_trash and to_trash:
            self.in_trash = True
            self.deleted_date_time = now()
            self.save()
        else:
            for version in self.versions.all():
                version.delete()

            return super(Document, self).delete(*args, **kwargs)

    def exists(self):
        """
        Returns a boolean value that indicates if the document's
        latest version file exists in storage
        """
        latest_version = self.latest_version
        if latest_version:
            return latest_version.exists()
        else:
            return False

    def get_absolute_url(self):
        return reverse(
            viewname='documents:document_preview',
            kwargs={'document_id': self.pk}
        )

    def get_api_image_url(self, *args, **kwargs):
        latest_version = self.latest_version
        if latest_version:
            return latest_version.get_api_image_url(*args, **kwargs)

    def get_duplicates(self):
        try:
            return DuplicatedDocument.objects.get(document=self).documents.all()
        except DuplicatedDocument.DoesNotExist:
            return Document.objects.none()

    def get_page_count(self):
        return self.pages.count()
    get_page_count.short_description = _('Pages')

    def get_rendered_deleted_date_time(self):
        return Template('{{ instance.deleted_date_time }}').render(
            context=Context({'instance': self})
        )
    get_rendered_deleted_date_time.short_description = _(
        'Date and time trashed'
    )

    def invalidate_cache(self):
        for document_version in self.versions.all():
            document_version.invalidate_cache()

    @property
    def is_in_trash(self):
        return self.in_trash

    def natural_key(self):
        return (self.uuid,)
    natural_key.dependencies = ['documents.DocumentType']

    def new_version(self, file_object, comment=None, _user=None):
        logger.info('Creating new document version for document: %s', self)
        DocumentVersion = apps.get_model(
            app_label='documents', model_name='DocumentVersion'
        )

        document_version = DocumentVersion(
            document=self, comment=comment or '', file=File(file_object)
        )
        document_version.save(_user=_user)

        logger.info('New document version queued for document: %s', self)
        return document_version

    def open(self, *args, **kwargs):
        """
        Return a file descriptor to a document's file irrespective of
        the storage backend
        """
        return self.latest_version.open(*args, **kwargs)

    def restore(self):
        self.in_trash = False
        self.save()

    def save(self, *args, **kwargs):
        user = kwargs.pop('_user', None)
        _commit_events = kwargs.pop('_commit_events', True)
        new_document = not self.pk
        super(Document, self).save(*args, **kwargs)

        if new_document:
            if user:
                self.add_as_recent_document_for_user(user)
                event_document_create.commit(
                    actor=user, target=self, action_object=self.document_type
                )
            else:
                event_document_create.commit(
                    target=self, action_object=self.document_type
                )
        else:
            if _commit_events:
                event_document_properties_edit.commit(actor=user, target=self)

    def save_to_file(self, *args, **kwargs):
        return self.latest_version.save_to_file(*args, **kwargs)

    def set_document_type(self, document_type, force=False, _user=None):
        has_changed = self.document_type != document_type

        self.document_type = document_type

        with transaction.atomic():
            self.save()
            if has_changed or force:
                post_document_type_change.send(
                    sender=self.__class__, instance=self
                )

                event_document_type_change.commit(actor=_user, target=self)
                if _user:
                    self.add_as_recent_document_for_user(user=_user)

    @property
    def size(self):
        return self.latest_version.size

    # Compatibility methods

    @property
    def checksum(self):
        return self.latest_version.checksum

    @property
    def date_updated(self):
        return self.latest_version.timestamp

    @property
    def file_mime_encoding(self):
        return self.latest_version.encoding

    @property
    def file_mimetype(self):
        return self.latest_version.mimetype

    @property
    def latest_version(self):
        return self.versions.order_by('timestamp').last()

    @property
    def page_count(self):
        return self.latest_version.page_count

    @property
    def pages(self):
        try:
            return self.latest_version.pages
        except AttributeError:
            # Document has no version yet
            DocumentPage = apps.get_model(
                app_label='documents', model_name='DocumentPage'
            )
            return DocumentPage.objects.none()


@python_2_unicode_compatible
class DuplicatedDocument(models.Model):
    document = models.ForeignKey(
        on_delete=models.CASCADE, related_name='duplicates', to=Document,
        verbose_name=_('Document')
    )
    documents = models.ManyToManyField(
        to=Document, verbose_name=_('Duplicated documents')
    )
    datetime_added = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_('Added')
    )

    objects = DuplicatedDocumentManager()

    class Meta:
        verbose_name = _('Duplicated document')
        verbose_name_plural = _('Duplicated documents')

    def __str__(self):
        return force_text(self.document)


class DuplicatedDocumentProxy(Document):
    class Meta:
        proxy = True
        verbose_name = _('Duplicated document')
        verbose_name_plural = _('Duplicated documents')

    def get_duplicate_count(self, user):
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view, queryset=self.get_duplicates(),
            user=user
        )
        return queryset.count()


@python_2_unicode_compatible
class FavoriteDocument(models.Model):
    """
    Keeps a list of the favorited documents of a given user
    """
    user = models.ForeignKey(
        db_index=True, editable=False, on_delete=models.CASCADE,
        to=settings.AUTH_USER_MODEL, verbose_name=_('User')
    )
    document = models.ForeignKey(
        editable=False, on_delete=models.CASCADE, related_name='favorites',
        to=Document, verbose_name=_('Document')
    )

    objects = FavoriteDocumentManager()

    class Meta:
        verbose_name = _('Favorite document')
        verbose_name_plural = _('Favorite documents')

    def __str__(self):
        return force_text(self.document)

    def natural_key(self):
        return (self.document.natural_key(), self.user.natural_key())
    natural_key.dependencies = ['documents.Document', settings.AUTH_USER_MODEL]


@python_2_unicode_compatible
class RecentDocument(models.Model):
    """
    Keeps a list of the n most recent accessed or created document for
    a given user
    """
    user = models.ForeignKey(
        db_index=True, editable=False, on_delete=models.CASCADE,
        to=settings.AUTH_USER_MODEL, verbose_name=_('User')
    )
    document = models.ForeignKey(
        editable=False, on_delete=models.CASCADE, related_name='recent',
        to=Document, verbose_name=_('Document')
    )
    datetime_accessed = models.DateTimeField(
        auto_now=True, db_index=True, verbose_name=_('Accessed')
    )

    objects = RecentDocumentManager()

    class Meta:
        ordering = ('-datetime_accessed',)
        verbose_name = _('Recent document')
        verbose_name_plural = _('Recent documents')

    def __str__(self):
        return force_text(self.document)

    def natural_key(self):
        return (self.datetime_accessed, self.document.natural_key(), self.user.natural_key())
    natural_key.dependencies = ['documents.Document', settings.AUTH_USER_MODEL]


class TrashedDocument(Document):
    objects = TrashCanManager()

    class Meta:
        proxy = True

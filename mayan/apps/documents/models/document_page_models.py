from __future__ import absolute_import, unicode_literals

import logging

from furl import furl

from django.db import models
from django.urls import reverse
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from mayan.apps.converter import (
    BaseTransformation, TransformationResize, TransformationRotate,
    TransformationZoom
)
from mayan.apps.converter.literals import DEFAULT_ROTATION, DEFAULT_ZOOM_LEVEL
from mayan.apps.converter.models import Transformation
from mayan.apps.converter.utils import get_converter_class

from ..managers import DocumentPageManager
from ..settings import (
    setting_disable_base_image_cache, setting_disable_transformed_image_cache,
    setting_display_height, setting_display_width, setting_zoom_max_level,
    setting_zoom_min_level
)

from .document_version_models import DocumentVersion

__all__ = ('DocumentPage', 'DocumentPageSearchResult')
logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class DocumentPage(models.Model):
    """
    Model that describes a document version page
    """
    document_version = models.ForeignKey(
        on_delete=models.CASCADE, related_name='pages', to=DocumentVersion,
        verbose_name=_('Document version')
    )
    page_number = models.PositiveIntegerField(
        db_index=True, default=1, editable=False,
        verbose_name=_('Page number')
    )

    objects = DocumentPageManager()

    class Meta:
        ordering = ('page_number',)
        verbose_name = _('Document page')
        verbose_name_plural = _('Document pages')

    def __str__(self):
        return self.get_label()

    @cached_property
    def cache_partition(self):
        partition, created = self.document_version.cache.partitions.get_or_create(
            name=self.uuid
        )
        return partition

    def delete(self, *args, **kwargs):
        self.invalidate_cache()
        super(DocumentPage, self).delete(*args, **kwargs)

    def detect_orientation(self):
        with self.document_version.open() as file_object:
            converter = get_converter_class()(
                file_object=file_object,
                mime_type=self.document_version.mimetype
            )
            return converter.detect_orientation(
                page_number=self.page_number
            )

    @cached_property
    def document(self):
        return self.document_version.document

    def generate_image(self, *args, **kwargs):
        transformation_list = self.get_combined_transformation_list(*args, **kwargs)
        combined_cache_filename = BaseTransformation.combine(transformation_list)

        # Check is transformed image is available
        logger.debug('transformations cache filename: %s', combined_cache_filename)

        if not setting_disable_transformed_image_cache.value and self.cache_partition.get_file(filename=combined_cache_filename):
            logger.debug(
                'transformations cache file "%s" found', combined_cache_filename
            )
        else:
            logger.debug(
                'transformations cache file "%s" not found', combined_cache_filename
            )
            image = self.get_image(transformations=transformation_list)
            with self.cache_partition.create_file(filename=combined_cache_filename) as file_object:
                file_object.write(image.getvalue())

        return combined_cache_filename

    def get_absolute_url(self):
        return reverse(
            viewname='documents:document_page_view',
            kwargs={'document_page_id': self.pk}
        )

    def get_api_image_url(self, *args, **kwargs):
        """
        Create an unique URL combining:
        - the page's image URL
        - the interactive argument
        - a hash from the server side and interactive transformations
        The purpose of this unique URL is to allow client side caching
        if document page images.
        """
        transformations_hash = BaseTransformation.combine(
            transformations=self.get_combined_transformation_list(
                *args, **kwargs
            )
        )

        transformations = kwargs.pop('transformations', None)

        final_url = furl()
        final_url.args = kwargs
        final_url.path = reverse(
            viewname='rest_api:document_page-image', kwargs={
                'document_id': self.document.pk,
                'document_version_id': self.document_version.pk,
                'document_page_id': self.pk
            }
        )
        final_url.args['_hash'] = transformations_hash
        count = 1
        for transformation in transformations or []:
            name, kwargs = transformation.serialize().split(';')

            final_url.args['transformation_{}_name'.format(count)] = name
            final_url.args['transformation_{}_kwargs'.format(count)] = kwargs
            count = count + 1

        return final_url.tostr()

    def get_combined_transformation_list(self, *args, **kwargs):
        """
        Return a list of transformation containing the server side
        document page transformation as well as tranformations created
        from the arguments as transient interactive transformation.
        """
        # Convert arguments into transformations
        transformations = kwargs.get('transformations', [])

        # Set sensible defaults if the argument is not specified or if the
        # argument is None
        width = kwargs.get('width', setting_display_width.value) or setting_display_width.value
        height = kwargs.get('height', setting_display_height.value) or setting_display_height.value
        rotation = kwargs.get('rotation', DEFAULT_ROTATION) or DEFAULT_ROTATION
        zoom_level = kwargs.get('zoom', DEFAULT_ZOOM_LEVEL) or DEFAULT_ZOOM_LEVEL

        if zoom_level < setting_zoom_min_level.value:
            zoom_level = setting_zoom_min_level.value

        if zoom_level > setting_zoom_max_level.value:
            zoom_level = setting_zoom_max_level.value

        # Generate transformation hash
        transformation_list = []

        # Stored transformations first
        for stored_transformation in Transformation.objects.get_for_model(self, as_classes=True):
            transformation_list.append(stored_transformation)

        # Interactive transformations second
        for transformation in transformations:
            transformation_list.append(transformation)

        if rotation:
            transformation_list.append(
                TransformationRotate(degrees=rotation)
            )

        if width:
            transformation_list.append(
                TransformationResize(width=width, height=height)
            )

        if zoom_level:
            transformation_list.append(TransformationZoom(percent=zoom_level))

        return transformation_list

    def get_image(self, transformations=None):
        cache_filename = 'base_image'
        logger.debug('Page cache filename: %s', cache_filename)

        cache_file = self.cache_partition.get_file(filename=cache_filename)
        if not setting_disable_base_image_cache.value and cache_file:
            logger.debug('Page cache file "%s" found', cache_filename)
            converter = get_converter_class()(
                file_object=cache_file.open()
            )

            converter.seek(0)
        else:
            logger.debug('Page cache file "%s" not found', cache_filename)

            converter = get_converter_class()(
                file_object=self.document_version.get_intermidiate_file()
            )
            converter.seek(page_number=self.page_number - 1)

            page_image = converter.get_page()

            with self.cache_partition.create_file(filename=cache_filename) as file_object:
                file_object.write(page_image.getvalue())

        for transformation in transformations:
            converter.transform(transformation=transformation)

        return converter.get_page()

    def get_label(self):
        return _(
            'Page %(page_num)d out of %(total_pages)d of %(document)s'
        ) % {
            'document': force_text(self.document),
            'page_num': self.page_number,
            'total_pages': self.document_version.pages.count()
        }
    get_label.short_description = _('Label')

    def invalidate_cache(self):
        self.cache_partition.purge()

    @property
    def is_in_trash(self):
        return self.document.is_in_trash

    def natural_key(self):
        return (self.page_number, self.document_version.natural_key())
    natural_key.dependencies = ['documents.DocumentVersion']

    @property
    def siblings(self):
        return DocumentPage.objects.filter(
            document_version=self.document_version
        )

    @cached_property
    def uuid(self):
        """
        Make cache UUID a mix of version UUID and page ID to avoid using stale
        images
        """
        return '{}-{}'.format(self.document_version.uuid, self.pk)


class DocumentPageSearchResult(DocumentPage):
    class Meta:
        ordering = ('document_version__document', 'page_number')
        proxy = True
        verbose_name = _('Document page')
        verbose_name_plural = _('Document pages')

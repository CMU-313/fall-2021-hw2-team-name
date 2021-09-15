from __future__ import unicode_literals

import logging
import random

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import OperationalError

from mayan.apps.converter.transformations import BaseTransformation
from mayan.apps.lock_manager import LockError
from mayan.apps.lock_manager.decorators import retry_on_lock_error
from mayan.celery import app

from .literals import (
    TASK_GENERATE_DODCUMENT_PAGE_IMAGE_RETRIES, UPDATE_PAGE_COUNT_RETRY_DELAY,
    UPLOAD_NEW_VERSION_RETRY_DELAY
)

logger = logging.getLogger(__name__)


@app.task(ignore_result=True)
def task_clean_empty_duplicate_lists():
    DuplicatedDocument = apps.get_model(
        app_label='documents', model_name='DuplicatedDocument'
    )
    DuplicatedDocument.objects.clean_empty_duplicate_lists()


@app.task(ignore_result=True)
def task_check_delete_periods():
    DocumentType = apps.get_model(
        app_label='documents', model_name='DocumentType'
    )

    DocumentType.objects.check_delete_periods()


@app.task(ignore_result=True)
def task_check_trash_periods():
    DocumentType = apps.get_model(
        app_label='documents', model_name='DocumentType'
    )

    DocumentType.objects.check_trash_periods()


@app.task(ignore_result=True)
def task_clear_image_cache():
    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )

    logger.info('Starting document cache invalidation')
    Document.objects.invalidate_cache()
    logger.info('Finished document cache invalidation')


@app.task(ignore_result=True)
def task_delete_document(deleted_document_id):
    DeletedDocument = apps.get_model(
        app_label='documents', model_name='DeletedDocument'
    )

    logger.debug('Executing')
    deleted_document = DeletedDocument.objects.get(pk=deleted_document_id)
    deleted_document.delete()
    logger.debug('Finshed')


@app.task(ignore_result=True)
def task_delete_stubs():
    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )

    logger.info('Executing')
    Document.passthrough.delete_stubs()
    logger.info('Finshed')


@app.task(bind=True, max_retries=TASK_GENERATE_DODCUMENT_PAGE_IMAGE_RETRIES)
def task_generate_document_page_image(self, document_page_id, transformation_list=None, *args, **kwargs):
    """
    Arguments:
        * transformation_list: List of dictionaties with keys: name and kwargs
        * args, kwargs: "width, height, zoom, rotation
    """
    DocumentPage = apps.get_model(
        app_label='documents', model_name='DocumentPage'
    )

    document_page = DocumentPage.objects.get(pk=document_page_id)

    transformations = []
    for transformation in transformation_list or []:
        transformations.append(
            BaseTransformation.get(
                name=transformation['name']
            )(**transformation.get('kwargs', {}))
        )

    def task_core_function():
        return document_page.generate_image(
            transformations=transformations, *args, **kwargs
        )

    if self.request.is_eager:
        # Task is running on eager mode, probably in development mode, so
        # retry the task manually.
        @retry_on_lock_error(
            retries=TASK_GENERATE_DODCUMENT_PAGE_IMAGE_RETRIES
        )
        def retry_task():
            return task_core_function()

        return retry_task()
    else:
        # Setup retrying the task via Celery
        try:
            return task_core_function()
        except LockError as exception:
            countdown = 2.0 ** self.request.retries
            countdown = random.randrange(countdown + 1)
            raise self.retry(countdown=countdown, exc=exception)


@app.task(ignore_result=True)
def task_scan_duplicates_all():
    DuplicatedDocument = apps.get_model(
        app_label='documents', model_name='DuplicatedDocument'
    )

    DuplicatedDocument.objects.scan()


@app.task(ignore_result=True)
def task_scan_duplicates_for(document_id):
    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )
    DuplicatedDocument = apps.get_model(
        app_label='documents', model_name='DuplicatedDocument'
    )

    document = Document.objects.get(pk=document_id)

    DuplicatedDocument.objects.scan_for(document=document)


@app.task(bind=True, default_retry_delay=UPDATE_PAGE_COUNT_RETRY_DELAY, ignore_result=True)
def task_update_page_count(self, version_id):
    DocumentVersion = apps.get_model(
        app_label='documents', model_name='DocumentVersion'
    )

    document_version = DocumentVersion.objects.get(pk=version_id)
    try:
        document_version.update_page_count()
    except OperationalError as exception:
        logger.warning(
            'Operational error during attempt to update page count for '
            'document version: %s; %s. Retrying.', document_version,
            exception
        )
        raise self.retry(exc=exception)


@app.task(bind=True, default_retry_delay=UPLOAD_NEW_VERSION_RETRY_DELAY, ignore_result=True)
def task_upload_new_version(self, document_id, shared_uploaded_file_id, user_id, comment=None):
    SharedUploadedFile = apps.get_model(
        app_label='common', model_name='SharedUploadedFile'
    )

    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )

    DocumentVersion = apps.get_model(
        app_label='documents', model_name='DocumentVersion'
    )

    try:
        document = Document.passthrough.get(pk=document_id)
        shared_file = SharedUploadedFile.objects.get(
            pk=shared_uploaded_file_id
        )
        if user_id:
            user = get_user_model().objects.get(pk=user_id)
        else:
            user = None

    except OperationalError as exception:
        logger.warning(
            'Operational error during attempt to retrieve shared data for '
            'new document version for:%s; %s. Retrying.', document, exception
        )
        raise self.retry(exc=exception)

    with shared_file.open() as file_object:
        document_version = DocumentVersion(
            document=document, comment=comment or '', file=file_object
        )
        try:
            document_version.save(_user=user)
        except Warning as warning:
            # New document version are blocked
            logger.info(
                'Warning during attempt to create new document version for '
                'document: %s; %s', document, warning
            )
            shared_file.delete()
        except OperationalError as exception:
            logger.warning(
                'Operational error during attempt to create new document '
                'version for document: %s; %s. Retrying.', document, exception
            )
            raise self.retry(exc=exception)
        except Exception as exception:
            # This except and else block emulate a finally:
            logger.error(
                'Unexpected error during attempt to create new document '
                'version for document: %s; %s', document, exception
            )
            try:
                shared_file.delete()
            except OperationalError as exception:
                logger.warning(
                    'Operational error during attempt to delete shared '
                    'file: %s; %s.', shared_file, exception
                )
        else:
            try:
                shared_file.delete()
            except OperationalError as exception:
                logger.warning(
                    'Operational error during attempt to delete shared '
                    'file: %s; %s.', shared_file, exception
                )

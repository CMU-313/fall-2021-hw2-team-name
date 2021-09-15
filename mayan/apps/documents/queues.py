from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.queues import queue_tools
from mayan.apps.task_manager.classes import CeleryQueue

queue_converter = CeleryQueue(
    label=_('Converter'), name='converter', transient=True
)
queue_documents_periodic = CeleryQueue(
    label=_('Documents periodic'), name='documents_periodic', transient=True
)
queue_uploads = CeleryQueue(
    label=_('Uploads'), name='uploads'
)
queue_documents = CeleryQueue(
    label=_('Documents'), name='documents'
)

queue_converter.add_task_type(
    label=_('Generate document page image'),
    name='mayan.apps.documents.tasks.task_generate_document_page_image'
)

queue_documents.add_task_type(
    label=_('Delete a document'),
    name='mayan.apps.documents.tasks.task_delete_document'
)
queue_documents.add_task_type(
    label=_('Clean empty duplicate lists'),
    name='mayan.apps.documents.tasks.task_clean_empty_duplicate_lists'
)

queue_documents_periodic.add_task_type(
    label=_('Check document type delete periods'),
    name='mayan.apps.documents.tasks.task_check_delete_periods'
)
queue_documents_periodic.add_task_type(
    label=_('Check document type trash periods'),
    name='mayan.apps.documents.tasks.task_check_trash_periods'
)
queue_documents_periodic.add_task_type(
    label=_('Delete document stubs'),
    name='mayan.apps.documents.tasks.task_delete_stubs'
)

queue_tools.add_task_type(
    label=_('Clear image cache'),
    name='mayan.apps.documents.tasks.task_clear_image_cache'
)

queue_uploads.add_task_type(
    label=_('Update document page count'),
    name='mayan.apps.documents.tasks.task_update_page_count'
)
queue_uploads.add_task_type(
    label=_('Upload new document version'),
    name='mayan.apps.documents.tasks.task_upload_new_version'
)

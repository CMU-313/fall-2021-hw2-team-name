from __future__ import unicode_literals

from django.apps import apps
from django.utils.encoding import force_text


def get_document_content_iterator(document):
    latest_version = document.latest_version

    if latest_version:
        return get_document_version_content_iterator(
            document_version=latest_version
        )


def get_document_version_content_iterator(document_version):
    DocumentPageOCRContent = apps.get_model(
        app_label='ocr', model_name='DocumentPageOCRContent'
    )

    for page in document_version.pages.all():
        try:
            page_content = page.ocr_content.content
        except DocumentPageOCRContent.DoesNotExist:
            return
        else:
            yield force_text(page_content)

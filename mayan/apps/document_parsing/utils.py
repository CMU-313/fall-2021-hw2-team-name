from __future__ import unicode_literals

from django.apps import apps
from django.utils.encoding import force_text
from django.utils.html import conditional_escape


def get_document_content_iterator(document):
    latest_version = document.latest_version

    if latest_version:
        return get_document_version_content_iterator(
            document_version=latest_version
        )


def get_document_version_content_iterator(document_version):
    DocumentPageContent = apps.get_model(
        app_label='document_parsing', model_name='DocumentPageContent'
    )

    for page in document_version.pages.all():
        try:
            page_content = page.content.content
        except DocumentPageContent.DoesNotExist:
            return
        else:
            yield conditional_escape(force_text(page_content))

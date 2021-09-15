import logging

from PIL import Image

from django.contrib import messages
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _, ungettext

from mayan.apps.documents.models import Document
from mayan.apps.storage.models import SharedUploadedFile
from mayan.apps.views.generics import SingleObjectDownloadView

logger = logging.getLogger(name=__name__)


class DocumentExportDownloadView(SingleObjectDownloadView):
    model = Document
    pk_url_kwarg = 'document_id'

    def _save_page(self, page, filename, append=False):
        cache_filename = page.generate_image()
        Image.open(
            page.cache_partition.get_file(filename=cache_filename).open()
        ).save(filename, format='PDF', append=append, resolution=300.0)

    def get_download_file_object(self):
        temp_filename = '/tmp/pdf_temp.pdf'

        first_page = self.object.pages_valid.first()
        self._save_page(page=first_page, filename=temp_filename)

        for page in self.object.pages_valid[1:]:
            self._save_page(page=page, filename=temp_filename, append=True)

        return open(temp_filename, mode='rb')

    def get_download_filename(self):
        return '{}.pdf'.format(force_text(self.object))

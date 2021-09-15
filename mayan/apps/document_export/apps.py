from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig


class DocumentExportApp(MayanAppConfig):
    app_namespace = 'document_export'
    app_url = 'document_export'
    name = 'mayan.apps.document_export'
    verbose_name = _('Document export')

    def ready(self, *args, **kwargs):
        super().ready(*args, **kwargs)

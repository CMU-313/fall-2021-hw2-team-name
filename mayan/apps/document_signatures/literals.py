from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

SIGNATURE_TYPE_DETACHED = 1
SIGNATURE_TYPE_EMBEDDED = 2
SIGNATURE_TYPE_CHOICES = (
    (SIGNATURE_TYPE_DETACHED, _('Detached')),
    (SIGNATURE_TYPE_EMBEDDED, _('Embedded')),
)

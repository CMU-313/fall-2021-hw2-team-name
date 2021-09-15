from __future__ import unicode_literals

from django.shortcuts import reverse


def method_get_absolute_url(self):
    return reverse(viewname='user_management:user_details', args=(self.pk,))

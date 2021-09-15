from __future__ import unicode_literals

from django.db import models


class DocumentTagManager(models.Manager):
    def get_for(self, document):
        return self.filter(document=document)

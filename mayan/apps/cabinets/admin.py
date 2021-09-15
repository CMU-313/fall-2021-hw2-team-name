from __future__ import unicode_literals

from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from .models import Cabinet


@admin.register(Cabinet)
class CabinetAdmin(MPTTModelAdmin):
    filter_horizontal = ('documents',)
    list_display = ('label',)

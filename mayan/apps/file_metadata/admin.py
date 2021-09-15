from __future__ import unicode_literals

from django.contrib import admin

from .models import StoredDriver


@admin.register(StoredDriver)
class StoredDriverAdmin(admin.ModelAdmin):
    list_display = ('internal_name', 'label', 'driver_path')

    def label(self, instance):
        return instance.driver_label

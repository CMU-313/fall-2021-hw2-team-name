from django.contrib import admin

from .models import ReviewerForm


@admin.register(ReviewerForm)
class ReviewerFormAdmin(admin.ModelAdmin):
    filter_horizontal = ('documents',)
    list_display = ('label',)

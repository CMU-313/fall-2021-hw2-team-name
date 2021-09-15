from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models

import mayan.apps.documents.models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0042_auto_20180403_0702'),
    ]

    operations = [
        migrations.AlterField(
            field=models.CharField(
                blank=True, editable=False, max_length=64, null=True,
                verbose_name='Encoding'
            ),
            model_name='documentversion', name='encoding',
        ),
        migrations.AlterField(
            field=models.FileField(
                storage=django.core.files.storage.FileSystemStorage(
                    location=b'/home/rosarior/development/mayan-edms/mayan/media/document_storage'
                ), upload_to=mayan.apps.documents.utils.document_uuid_function,
                verbose_name='File'
            ),
            model_name='documentversion', name='file',
        ),
        migrations.AlterField(
            field=models.CharField(
                blank=True, editable=False, max_length=255, null=True,
                verbose_name='MIME type'
            ),
            model_name='documentversion', name='mimetype',
        ),
    ]

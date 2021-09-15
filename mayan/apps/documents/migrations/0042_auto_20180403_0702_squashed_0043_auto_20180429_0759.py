from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models
import mayan.apps.documents.utils


class Migration(migrations.Migration):

    replaces = [
        ('documents', '0042_auto_20180403_0702'),
        ('documents', '0043_auto_20180429_0759')
    ]

    dependencies = [
        ('documents', '0041_auto_20170823_1855'),
    ]

    operations = [
        migrations.AlterField(
            field=models.FileField(
                storage=django.core.files.storage.FileSystemStorage(
                    location=b'mayan/media/document_storage'
                ), upload_to=mayan.apps.documents.utils.document_uuid_function,
                verbose_name='File'
            ), model_name='documentversion', name='file',
        ),
        migrations.AlterField(
            model_name='documentversion',
            name='encoding',
            field=models.CharField(blank=True, editable=False, max_length=64, null=True, verbose_name='Encoding'),
        ),
        migrations.AlterField(
            field=models.FileField(
                storage=django.core.files.storage.FileSystemStorage(
                    location=b'/home/rosarior/development/mayan-edms/mayan/media/document_storage'
                ), upload_to=mayan.apps.documents.utils.document_uuid_function,
                verbose_name='File'
            ), model_name='documentversion', name='file',
        ),
        migrations.AlterField(
            model_name='documentversion',
            name='mimetype',
            field=models.CharField(blank=True, editable=False, max_length=255, null=True, verbose_name='MIME type'),
        ),
    ]

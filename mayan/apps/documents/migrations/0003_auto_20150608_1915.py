from __future__ import unicode_literals

from django.core.files.storage import FileSystemStorage
from django.db import migrations, models

import mayan.apps.documents.models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_auto_20150608_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='uuid',
            field=models.CharField(
                default=mayan.apps.documents.utils.document_uuid_function,
                editable=False, max_length=48,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='documentversion',
            name='file',
            field=models.FileField(
                storage=FileSystemStorage(),
                upload_to=mayan.apps.documents.utils.document_uuid_function,
                verbose_name='File'
            ),
            preserve_default=True,
        ),
    ]

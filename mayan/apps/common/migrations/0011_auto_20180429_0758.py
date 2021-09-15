from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models

import mayan.apps.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0010_auto_20180403_0702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shareduploadedfile',
            name='file',
            field=models.FileField(
                storage=django.core.files.storage.FileSystemStorage(
                    location=b'/home/rosarior/development/mayan-edms/mayan/media/shared_files'
                ), upload_to=mayan.apps.common.models.upload_to,
                verbose_name='File'
            ),
        ),
    ]

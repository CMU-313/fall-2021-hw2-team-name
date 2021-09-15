from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models

import mayan.apps.common.models


class Migration(migrations.Migration):

    replaces = [
        ('common', '0010_auto_20180403_0702'),
        ('common', '0011_auto_20180429_0758')
    ]

    dependencies = [
        ('common', '0009_auto_20180402_0339'),
    ]

    operations = [
        migrations.AlterField(
            field=models.FileField(
                storage=django.core.files.storage.FileSystemStorage(
                    location='/home/rosarior/development/mayan-edms/mayan/media/shared_files'
                ), upload_to=mayan.apps.common.models.upload_to,
                verbose_name='File'
            ), model_name='shareduploadedfile', name='file',
        ),
    ]

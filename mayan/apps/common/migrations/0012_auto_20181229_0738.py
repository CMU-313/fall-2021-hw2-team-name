from __future__ import unicode_literals

from django.db import migrations, models

import mayan.apps.common.classes
import mayan.apps.common.models
import mayan.apps.storage.classes


class Migration(migrations.Migration):
    dependencies = [
        ('common', '0010_auto_20180403_0702_squashed_0011_auto_20180429_0758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shareduploadedfile',
            name='file',
            field=models.FileField(
                storage=mayan.apps.storage.classes.FakeStorageSubclass(),
                upload_to=mayan.apps.common.models.upload_to,
                verbose_name='File'
            ),
        ),
    ]

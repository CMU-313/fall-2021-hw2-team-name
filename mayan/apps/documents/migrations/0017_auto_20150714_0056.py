from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0016_auto_20150708_0325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='date_added',
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, verbose_name='Added'
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='documentversion',
            name='timestamp',
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, verbose_name='Timestamp'
            ),
            preserve_default=True,
        ),
    ]

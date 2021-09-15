from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0023_auto_20150715_0259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentversion',
            name='comment',
            field=models.TextField(
                blank=True, default='', verbose_name='Comment'
            ),
            preserve_default=True,
        ),
    ]

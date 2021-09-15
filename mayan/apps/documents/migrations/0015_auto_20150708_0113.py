from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0014_auto_20150708_0107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documenttype',
            name='label',
            field=models.CharField(
                max_length=32, unique=True, verbose_name='Label'
            ),
            preserve_default=True,
        ),
    ]

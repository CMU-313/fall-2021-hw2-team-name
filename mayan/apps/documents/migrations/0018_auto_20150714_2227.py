from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0017_auto_20150714_0056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='description',
            field=models.TextField(
                blank=True, default='', verbose_name='Description'
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='document',
            name='label',
            field=models.CharField(
                blank=True, default='', db_index=True,
                help_text='The name of the document', max_length=255,
                verbose_name='Label'
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='documentversion',
            name='comment',
            field=models.TextField(
                blank=True, default='', verbose_name='Comment'
            ),
            preserve_default=True,
        ),
    ]

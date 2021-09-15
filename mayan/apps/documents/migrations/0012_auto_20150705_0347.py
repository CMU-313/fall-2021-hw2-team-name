from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0011_auto_20150704_0508'),
    ]

    operations = [
        migrations.AlterField(
            field=models.DateTimeField(
                blank=True, null=True, verbose_name='Date and time trashed'
            ),
            model_name='document', name='deleted_date_time',
            preserve_default=True,
        ),
        migrations.AlterField(
            field=models.PositiveIntegerField(
                default=30, help_text='Amount of time after which documents '
                'of this type in the trash will be deleted.',
                verbose_name='Delete time period'
            ),
            model_name='documenttype', name='delete_time_period',
            preserve_default=True,
        ),
        migrations.AlterField(
            field=models.CharField(
                choices=[
                    ('days', 'Days'), ('hours', 'Hours'),
                    ('minutes', 'Minutes')
                ], default='days', max_length=8,
                verbose_name='Delete time unit'
            ),
            model_name='documenttype', name='delete_time_unit',
            preserve_default=True,
        ),
        migrations.AlterField(
            field=models.PositiveIntegerField(
                blank=True, help_text='Amount of time after which documents '
                'of this type will be moved to the trash.', null=True,
                verbose_name='Trash time period'
            ), model_name='documenttype', name='trash_time_period',
            preserve_default=True,
        ),
        migrations.AlterField(
            field=models.CharField(
                blank=True, choices=[
                    ('days', 'Days'), ('hours', 'Hours'),
                    ('minutes', 'Minutes')
                ], max_length=8, null=True, verbose_name='Trash time unit'
            ),
            model_name='documenttype', name='trash_time_unit',
            preserve_default=True
        ),
    ]

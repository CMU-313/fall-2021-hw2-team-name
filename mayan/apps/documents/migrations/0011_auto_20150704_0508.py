from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0010_auto_20150704_0054'),
    ]

    operations = [
        migrations.AddField(
            model_name='documenttype',
            name='delete_time_period',
            field=models.PositiveIntegerField(
                default=30, verbose_name='Delete time period'
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='documenttype',
            name='delete_time_unit',
            field=models.CharField(
                choices=[
                    ('days', 'Days'), ('hours', 'Hours'),
                    ('minutes', 'Minutes'), ('seconds', 'Seconds')
                ],
                default='days', max_length=8, verbose_name='Delete time unit'
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='documenttype',
            name='trash_time_period',
            field=models.PositiveIntegerField(
                blank=True, null=True, verbose_name='Trash time period'
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='documenttype',
            name='trash_time_unit',
            field=models.CharField(
                blank=True, choices=[
                    ('days', 'Days'), ('hours', 'Hours'),
                    ('minutes', 'Minutes'), ('seconds', 'Seconds')
                ], max_length=8, null=True, verbose_name='Trash time unit'
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            field=models.DateTimeField(
                verbose_name='Date and time trashed', blank=True
            ), model_name='document', name='deleted_date_time',
            preserve_default=True,
        ),
    ]

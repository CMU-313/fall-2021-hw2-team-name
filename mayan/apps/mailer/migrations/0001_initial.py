from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            bases=(models.Model,), fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'datetime', models.DateTimeField(
                        auto_now_add=True, verbose_name='Date time'
                    )
                ),
                (
                    'message', models.TextField(
                        blank=True, editable=False, verbose_name='Message'
                    )
                ),
            ], name='LogEntry', options={
                'get_latest_by': 'datetime', 'ordering': ('-datetime',),
                'verbose_name': 'Log entry',
                'verbose_name_plural': 'Log entries',
            },
        ),
    ]

from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailer', '0002_usermailer_usermailerlogentry'),
    ]

    operations = [
        migrations.AddField(
            field=models.BooleanField(default=True, verbose_name='Enabled'),
            model_name='usermailer', name='enabled',
        ),
        migrations.AlterField(
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='error_log', to='mailer.UserMailer',
                verbose_name='User mailer'
            ), model_name='usermailerlogentry', name='user_mailer',
        ),
    ]

from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_auto_20170802_0823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventsubscription',
            name='stored_event_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='event_subscriptions',
                to='events.StoredEventType', verbose_name='Event type'
            ),
        ),
    ]

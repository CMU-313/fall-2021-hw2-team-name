from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_signatures', '0005_auto_20160325_0748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signaturebasemodel',
            name='public_key_fingerprint',
            field=models.CharField(
                blank=True, editable=False, max_length=40,
                null=True, verbose_name='Public key fingerprint'
            ),
        ),
    ]

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0033_auto_20160325_0052'),
    ]

    operations = [
        migrations.AlterField(
            field=models.BooleanField(
                db_index=True, default=False, editable=False,
                verbose_name='In trash?'
            ),
            model_name='document', name='in_trash',
        ),
        migrations.AlterField(
            field=models.BooleanField(
                default=True, db_index=True, editable=False,
                help_text='A document stub is a document with an entry on '
                'the database but no file uploaded. This could be an '
                'interrupted upload or a deferred upload via the API.',
                verbose_name='Is stub?'
            ),
            model_name='document', name='is_stub',
        ),
    ]

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0026_auto_20150729_2140'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documenttypefilename',
            options={
                'ordering': ('filename',),
                'verbose_name': 'Quick rename template',
                'verbose_name_plural': 'Quick rename templates'
            },
        ),
        migrations.AlterField(
            field=models.BooleanField(
                default=True, editable=False, help_text='A document stub is '
                'a document with an entry on the database but no file '
                'uploaded. This could be an interrupted upload or a '
                'deferred upload via the API.',
                verbose_name='Is stub?'
            ), model_name='document', name='is_stub', preserve_default=True
        ),
        migrations.AlterField(
            field=models.CharField(
                db_index=True, max_length=128, verbose_name='Label'
            ), model_name='documenttypefilename', name='filename',
            preserve_default=True
        ),
    ]

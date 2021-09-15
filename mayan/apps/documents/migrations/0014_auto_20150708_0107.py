from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0013_document_is_stub'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documenttype',
            options={
                'ordering': ('label',), 'verbose_name': 'Document type',
                'verbose_name_plural': 'Documents types'
            },
        ),
        migrations.RenameField(
            model_name='documenttype',
            new_name='label',
            old_name='name'
        ),
    ]

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0048_auto_20181204_1835'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DocumentPageResult',
        ),
        migrations.CreateModel(
            name='DocumentPageSearchResult',
            fields=[
            ],
            options={
                'ordering': ('document_version__document', 'page_number'),
                'verbose_name': 'Document page',
                'proxy': True,
                'verbose_name_plural': 'Document pages',
                'indexes': [],
            },
            bases=('documents.documentpage',),
        ),
    ]

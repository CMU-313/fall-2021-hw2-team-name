from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0034_auto_20160509_2321'),
    ]

    operations = [
        migrations.CreateModel(
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID',
                    )
                ),
                (
                    'filename', models.CharField(
                        max_length=128, verbose_name='Filename'
                    )
                ),
            ], name='DocumentPageCachedImage', options={
                'verbose_name': 'Document page cached image',
                'verbose_name_plural': 'Document page cached images',
            },
        ),
        migrations.CreateModel(
            bases=('documents.documentpage',), fields=[],
            name='DocumentPageResult', options={
                'ordering': ('document_version__document', 'page_number'),
                'proxy': True, 'verbose_name': 'Document page',
                'verbose_name_plural': 'Document pages',
            },
        ),
        migrations.AddField(
            field=models.ForeignKey(
                related_name='cached_images', to='documents.DocumentPage',
                verbose_name='Document page'
            ),
            model_name='documentpagecachedimage', name='document_page',
        ),
    ]

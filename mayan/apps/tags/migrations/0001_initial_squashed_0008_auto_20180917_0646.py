from __future__ import unicode_literals

from django.db import migrations, models

import colorful.fields


class Migration(migrations.Migration):

    replaces = [
        ('tags', '0001_initial'),
        ('tags', '0002_tag_selection'),
        ('tags', '0003_remove_tag_color'),
        ('tags', '0004_auto_20150717_2336'),
        ('tags', '0005_auto_20150718_0616'),
        ('tags', '0006_documenttag'),
        ('tags', '0007_auto_20170118_1758'),
        ('tags', '0008_auto_20180917_0646')
    ]

    dependencies = [
        ('documents', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'label', models.CharField(
                        db_index=True, help_text='A short text used as the '
                        'tag name.', max_length=128, unique=True,
                        verbose_name='Label'
                    )
                ),
                (
                    'color', colorful.fields.RGBColorField(
                        help_text='The RGB color values for the tag.',
                        verbose_name='Color'
                    )
                ),
                (
                    'documents', models.ManyToManyField(
                        related_name='tags', to='documents.Document',
                        verbose_name='Documents'
                    )
                ),
            ], name='Tag', options={
                'ordering': ('label',),
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
        migrations.CreateModel(
            bases=('tags.tag',), fields=[], name='DocumentTag',
            options={
                'proxy': True, 'verbose_name': 'Document tag',
                'verbose_name_plural': 'Document tags',
            },
        ),
    ]

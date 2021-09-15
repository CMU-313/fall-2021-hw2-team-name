from __future__ import unicode_literals

import uuid

from django.db import connection, migrations, models
import django.db.models.deletion


def operation_convert_uuid_to_hex(apps, schema_editor):
    Document = apps.get_model('documents', 'Document')

    for document in Document.objects.using(schema_editor.connection.alias).all():
        document.uuid = uuid.UUID(document.uuid).hex
        document.save()


def operation_convert_uuid_model_field_to_native_minus_oracle(apps, schema_editor):
    if not schema_editor.connection.vendor == 'oracle':
        # Skip this migration for Oracle
        # GitHub issue #251
        migrations.AlterField(
            field=models.UUIDField(default=uuid.uuid4, editable=False),
            model_name='document', name='uuid',
        )


def operation_convert_uuid_db_field_to_native_postgresql(apps, schema_editor):
    if connection.vendor == 'postgresql':
        migrations.RunSQL(
            'ALTER TABLE documents_document ALTER COLUMN uuid SET '
            'DATA TYPE UUID USING uuid::uuid;'
        )


class Migration(migrations.Migration):

    replaces = [
        ('documents', '0029_auto_20160122_0755'),
        ('documents', '0030_auto_20160309_1837'),
        ('documents', '0031_convert_uuid'),
        ('documents', '0032_auto_20160315_0537'),
        ('documents', '0033_auto_20160325_0052'),
        ('documents', '0034_auto_20160509_2321'),
        ('documents', '0035_auto_20161102_0633'),
        ('documents', '0036_auto_20161222_0534'),
        ('documents', '0037_auto_20161231_0617')
    ]

    dependencies = [
        ('documents', '0028_newversionblock'),
    ]

    operations = [
        migrations.AlterField(
            field=models.CharField(
                blank=True, default='eng', max_length=8,
                verbose_name='Language'
            ), model_name='document', name='language',
        ),
        migrations.AlterField(
            field=models.PositiveIntegerField(
                blank=True, default=30, help_text='Amount of time after '
                'which documents of this type in the trash will be '
                'deleted.', null=True, verbose_name='Delete time period'
            ), model_name='documenttype', name='delete_time_period',
        ),
        migrations.AlterField(
            field=models.CharField(
                blank=True, choices=[
                    ('days', 'Days'), ('hours', 'Hours'),
                    ('minutes', 'Minutes')
                ], default='days', max_length=8, null=True,
                verbose_name='Delete time unit'
            ), model_name='documenttype', name='delete_time_unit',
        ),
        migrations.RunPython(
            code=operation_convert_uuid_to_hex,
        ),
        migrations.RunPython(
            code=operation_convert_uuid_model_field_to_native_minus_oracle,
        ),
        migrations.RunPython(
            code=operation_convert_uuid_db_field_to_native_postgresql,
        ),
        migrations.AlterModelOptions(
            name='documenttypefilename', options={
                'ordering': ('filename',), 'verbose_name': 'Quick label',
                'verbose_name_plural': 'Quick labels'
            },
        ),
        migrations.AlterField(
            field=models.BooleanField(
                db_index=True, default=False, editable=False,
                verbose_name='In trash?'
            ), model_name='document', name='in_trash',
        ),
        migrations.AlterField(
            field=models.BooleanField(
                db_index=True, default=True, editable=False, help_text='A '
                'document stub is a document with an entry on the database '
                'but no file uploaded. This could be an interrupted upload '
                'or a deferred upload via the API.', verbose_name='Is stub?'
            ), model_name='document', name='is_stub',
        ),
        migrations.CreateModel(
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
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
                on_delete=django.db.models.deletion.CASCADE,
                related_name='cached_images', to='documents.DocumentPage',
                verbose_name='Document page'
            ), model_name='documentpagecachedimage', name='document_page',
        ),
        migrations.RemoveField(
            model_name='newversionblock', name='document',
        ),
        migrations.DeleteModel(
            name='NewVersionBlock',
        ),
    ]

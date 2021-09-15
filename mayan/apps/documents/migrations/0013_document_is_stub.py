from __future__ import unicode_literals

from django.db import migrations, models


def operation_make_existing_documents_not_stubs(apps, schema_editor):
    Document = apps.get_model('documents', 'Document')

    for document in Document.objects.using(schema_editor.connection.alias).all():
        document.is_stub = False
        document.save()


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0012_auto_20150705_0347'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='is_stub',
            field=models.BooleanField(
                default=True, editable=False, verbose_name='Is stub?'
            ),
            preserve_default=True,
        ),
        migrations.RunPython(code=operation_make_existing_documents_not_stubs),
    ]

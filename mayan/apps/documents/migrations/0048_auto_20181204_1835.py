from __future__ import unicode_literals

from django.db import migrations


def operation_clear_old_cache(apps, schema_editor):
    DocumentPageCachedImage = apps.get_model(
        'documents', 'DocumentPageCachedImage'
    )

    for cached_image in DocumentPageCachedImage.objects.using(schema_editor.connection.alias).all():
        # Delete each cached image directly to trigger the physical deletion
        # of the stored file
        cached_image.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0047_auto_20180917_0737'),
    ]

    operations = [
        migrations.RunPython(code=operation_clear_old_cache),
        migrations.RemoveField(
            model_name='documentpagecachedimage',
            name='document_page',
        ),
        migrations.DeleteModel(
            name='DocumentPageCachedImage',
        ),
    ]

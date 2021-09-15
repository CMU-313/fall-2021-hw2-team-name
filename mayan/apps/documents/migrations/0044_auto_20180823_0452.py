from __future__ import unicode_literals

from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('documents', '0043_auto_20180429_0759'),
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
            ], name='FavoriteDocument', options={
                'verbose_name': 'Favorite document',
                'verbose_name_plural': 'Favorite documents',
            },
        ),
        migrations.AlterModelOptions(
            name='document', options={
                'ordering': ('label',), 'verbose_name': 'Document',
                'verbose_name_plural': 'Documents'
            },
        ),
        migrations.AlterField(
            field=models.ForeignKey(
                editable=False, on_delete=django.db.models.deletion.CASCADE,
                related_name='recent', to='documents.Document',
                verbose_name='Document'
            ), model_name='recentdocument', name='document',
        ),
        migrations.AddField(
            field=models.ForeignKey(
                editable=False, on_delete=django.db.models.deletion.CASCADE,
                related_name='favorites', to='documents.Document',
                verbose_name='Document'
            ), model_name='favoritedocument', name='document',
        ),
        migrations.AddField(
            field=models.ForeignKey(
                editable=False, on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL, verbose_name='User'
            ), model_name='favoritedocument', name='user',
        ),
    ]

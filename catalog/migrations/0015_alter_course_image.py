# Generated by Django 3.2 on 2021-04-21 11:16

import catalog.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0014_auto_20210420_0759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.ImageField(default=django.utils.timezone.now, upload_to=catalog.models.image_directory_path, verbose_name='obrázek'),
            preserve_default=False,
        ),
    ]
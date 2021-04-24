# Generated by Django 3.2 on 2021-04-24 18:02

import catalog.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0016_auto_20210424_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.ImageField(help_text='minimální rozměr 500x500 px', upload_to=catalog.models.image_directory_path, verbose_name='obrázek'),
        ),
        migrations.AlterField(
            model_name='weekschedule',
            name='hour',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(7), django.core.validators.MaxValueValidator(22)]),
        ),
    ]
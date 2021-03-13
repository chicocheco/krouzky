# Generated by Django 3.1.7 on 2021-03-10 18:57

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0010_auto_20210310_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from='title', unique_with=('organization__name',)),
        ),
    ]
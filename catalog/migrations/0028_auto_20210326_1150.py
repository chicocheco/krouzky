# Generated by Django 3.1.7 on 2021-03-26 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0027_auto_20210326_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='description',
            field=models.TextField(blank=True, verbose_name='popis'),
        ),
    ]
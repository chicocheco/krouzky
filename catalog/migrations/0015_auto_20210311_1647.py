# Generated by Django 3.1.7 on 2021-03-11 15:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0014_auto_20210311_1640'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agecategory',
            options={'verbose_name': 'Věková kategorie', 'verbose_name_plural': 'Věkové kategorie'},
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'verbose_name': 'Kroužek', 'verbose_name_plural': 'Kroužky'},
        ),
    ]
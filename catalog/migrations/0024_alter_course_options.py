# Generated by Django 3.2 on 2021-05-05 08:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0023_alter_course_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['-date_modified'], 'verbose_name': 'Aktivita', 'verbose_name_plural': 'Aktivity'},
        ),
    ]
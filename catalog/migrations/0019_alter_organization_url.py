# Generated by Django 3.2 on 2021-04-26 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0018_course_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='url',
            field=models.URLField(max_length=35, verbose_name='URL'),
        ),
    ]
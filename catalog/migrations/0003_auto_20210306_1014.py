# Generated by Django 3.1.7 on 2021-03-06 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20210306_1008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='capacity',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='hours',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='course',
            name='price',
            field=models.PositiveIntegerField(),
        ),
    ]
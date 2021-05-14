# Generated by Django 3.2 on 2021-05-14 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0029_auto_20210513_1833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Ke schválení'), ('PUBLISHED', 'Publikováno'), ('FINISHED', 'Ukončeno')], default='DRAFT', max_length=9, verbose_name='stav'),
        ),
    ]
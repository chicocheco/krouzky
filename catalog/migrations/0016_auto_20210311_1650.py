# Generated by Django 3.1.7 on 2021-03-11 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0015_auto_20210311_1647'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='topic',
            options={'verbose_name': 'Zaměření', 'verbose_name_plural': 'Zaměření'},
        ),
        migrations.AlterField(
            model_name='agecategory',
            name='age_from',
            field=models.PositiveIntegerField(verbose_name='od věku'),
        ),
        migrations.AlterField(
            model_name='agecategory',
            name='age_to',
            field=models.PositiveIntegerField(verbose_name='do věku'),
        ),
        migrations.AlterField(
            model_name='agecategory',
            name='name',
            field=models.CharField(max_length=30, verbose_name='název'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='name',
            field=models.CharField(max_length=50, verbose_name='název'),
        ),
    ]
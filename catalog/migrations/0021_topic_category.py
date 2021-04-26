# Generated by Django 3.2 on 2021-04-26 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0020_alter_organization_company_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='category',
            field=models.CharField(choices=[('MUSIC', 'Hudební'), ('ART', 'Umělecké'), ('LANG', 'Jazykové'), ('SPORT', 'Sportovní'), ('OTHER', 'Ostatní')], default='OTHER', max_length=5, verbose_name='Kategorie'),
        ),
    ]

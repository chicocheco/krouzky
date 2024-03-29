# Generated by Django 3.2.3 on 2021-06-18 11:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to=settings.AUTH_USER_MODEL, verbose_name='vedoucí'),
        ),
        migrations.AddField(
            model_name='course',
            name='week_schedule',
            field=models.ManyToManyField(blank=True, related_name='courses', to='catalog.WeekSchedule', verbose_name='týdenní rozvrh'),
        ),
    ]

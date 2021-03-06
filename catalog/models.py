from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Organization(models.Model):
    name = models.CharField(_('název organizace'), max_length=100, blank=False)
    company_id = models.CharField(_('IČO'), max_length=8, blank=False)
    vat_id = models.CharField(_('DIČ'), max_length=10, blank=False)
    address = models.CharField(_('adresa'), max_length=100, blank=False)
    town = models.CharField(_('město'), max_length=40, blank=False)
    zip_code = models.CharField(_('PSČ'), max_length=5, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class AgeCategory(models.Model):
    name = models.CharField(max_length=30, blank=False)
    age_from = models.IntegerField(blank=False)
    age_to = models.IntegerField(blank=False)

    class Meta:
        verbose_name_plural = 'Age Categories'

    def __str__(self):
        return f'{self.name} ({self.age_from}-{self.age_to})'


class Topic(models.Model):
    name = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField(null=False, blank=False)
    hours = models.PositiveIntegerField(null=False, blank=False)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='courses', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name='courses', on_delete=models.CASCADE)
    age_category = models.ForeignKey(AgeCategory, related_name='courses', on_delete=models.CASCADE)  # choices instead?
    topic = models.ManyToManyField(Topic)  # choices instead?
    date_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} [{self.organization.name}]'

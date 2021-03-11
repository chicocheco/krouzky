from django.conf import settings
from django.db import models
from django.urls import reverse
from autoslug import AutoSlugField
from django.utils.translation import gettext_lazy as _


class Organization(models.Model):
    name = models.CharField(_('název'), max_length=100, unique=True, blank=False)
    slug = models.SlugField(_('slug'), max_length=100)
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
    age_from = models.PositiveIntegerField(blank=False)
    age_to = models.PositiveIntegerField(blank=False)

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
    slug = AutoSlugField(populate_from='title')  # make unique with organization?
    description = models.TextField(blank=True)
    image = models.ImageField(null=True, upload_to='images/%Y/%m/%d')
    price = models.PositiveIntegerField(null=False, blank=False)
    hours = models.PositiveIntegerField(null=False, blank=False)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='courses', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name='courses', on_delete=models.CASCADE)
    age_category = models.ForeignKey(AgeCategory, related_name='courses', on_delete=models.CASCADE)
    topic = models.ManyToManyField(Topic)
    date_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} [{self.organization.name}]'

    def get_absolute_url(self):
        return reverse('',
                       args=[])
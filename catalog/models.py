from django.db import models
from django.conf import settings


class Organization(models.Model):
    founder = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)
    company_id = models.CharField(max_length=8, null=False, blank=False)
    vat_id = models.CharField(max_length=10, null=False, blank=False)
    address = models.CharField(max_length=100, null=False, blank=False)
    town = models.CharField(max_length=40, null=False, blank=False)
    zip_code = models.IntegerField(null=False, blank=False)


class AgeCategory(models.Model):
    name = models.CharField(max_length=30, null=False, blank=False)
    age_from = models.IntegerField(null=False, blank=False)
    age_to = models.IntegerField(null=False, blank=False)


class Topic(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)


class Course(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField(null=False, blank=False)
    hours = models.IntegerField(null=False, blank=False)
    capacity = models.IntegerField(null=True, blank=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='courses', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name='courses', on_delete=models.CASCADE)
    age_category = models.ForeignKey(AgeCategory, related_name='courses', on_delete=models.CASCADE)  # choices instead?
    topic = models.ManyToManyField(Topic)  # choices instead?

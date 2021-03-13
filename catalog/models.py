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
    date_created = models.DateTimeField(_('vytvořeno'), auto_now_add=True)

    class Meta:
        verbose_name = "Organizace"
        verbose_name_plural = "Organizace"

    def __str__(self):
        return self.name


class AgeCategory(models.Model):
    name = models.CharField(_('název'), max_length=30, blank=False)
    age_from = models.PositiveIntegerField(_('od věku'), blank=False)
    age_to = models.PositiveIntegerField(_('do věku'), blank=False)

    class Meta:
        verbose_name = 'Věková kategorie'
        verbose_name_plural = 'Věkové kategorie'

    def __str__(self):
        return f'{self.name} ({self.age_from}-{self.age_to})'


class Topic(models.Model):
    name = models.CharField(_('název'), max_length=50, blank=False)

    class Meta:
        verbose_name = 'Zaměření'
        verbose_name_plural = 'Zaměření'

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(_('název'), max_length=100, blank=False)
    slug = AutoSlugField(_('slug'), populate_from='title')  # make unique with organization?
    description = models.TextField(_('popis'), blank=True)
    image = models.ImageField(_('obrázek'), null=True, upload_to='images/%Y/%m/%d')
    price = models.PositiveIntegerField(_('cena'), null=False, blank=False)
    hours = models.PositiveIntegerField(_('počet hodin'), null=False, blank=False)
    capacity = models.PositiveIntegerField(_('kapacita'), null=True, blank=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL,
                                verbose_name='učitel', related_name='courses', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization,
                                     verbose_name='organizace', related_name='courses', on_delete=models.CASCADE)
    age_category = models.ForeignKey(AgeCategory,
                                     verbose_name='věková kategorie', related_name='courses', on_delete=models.CASCADE)
    topic = models.ManyToManyField(Topic, verbose_name='zaměření')
    date_modified = models.DateTimeField(_('upraveno'), auto_now=True)
    date_created = models.DateTimeField(_('vytvořeno'), auto_now_add=True)

    class Meta:
        verbose_name = 'Kroužek'
        verbose_name_plural = 'Kroužky'

    def __str__(self):
        return f'{self.title} [{self.organization.name}]'

    # def get_absolute_url(self):

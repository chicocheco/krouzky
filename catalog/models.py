from autoslug import AutoSlugField
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Organization(models.Model):
    name = models.CharField(_('název'), max_length=30, unique=True, blank=False)
    url = models.URLField(_('URL'), max_length=35, blank=True)
    slug = models.SlugField(_('slug'), max_length=30)
    company_id = models.CharField(_('IČO'), max_length=8, blank=False)
    vat_id = models.CharField(_('DIČ'), max_length=10, blank=True)
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


class WeekSchedule(models.Model):
    WEEKDAYS = {
        0: 'Pondělí',
        1: 'Úterý',
        2: 'Středa',
        3: 'Čtvrtek',
        4: 'Pátek',
        5: 'Sobota',
        6: 'Neděle',
    }
    day_of_week = models.PositiveSmallIntegerField(validators=[MaxValueValidator(6)])  # 0-6
    hour = models.PositiveSmallIntegerField(validators=[MaxValueValidator(23)])  # 7-23

    class Meta:
        ordering = ['hour', 'day_of_week']
        verbose_name = 'Týdenní rozvrh'
        verbose_name_plural = 'Týdenní rozvrh'
        unique_together = [['day_of_week', 'hour']]

    def __str__(self):
        return f'{self.WEEKDAYS[self.day_of_week]} {str(self.hour).zfill(2)}:00'

    # helper function
    def fill_table(self):
        for i in range(7, 23):
            for j in range(7):
                self.objects.create(day_of_week=j, hour=i)


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Course.Status.PUBLISHED)


def image_directory_path(instance, filename):
    return f'images/{instance.slug}.{filename.split(".")[-1]}'  # pathlib?


class Course(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Ke schválení')
        PUBLISHED = 'PUBLISHED', _('Publikováno')

    name = models.CharField(_('název'), max_length=50, blank=False)
    slug = AutoSlugField(_('slug'), populate_from='name')  # make unique with organization?
    description = models.TextField(_('popis'), blank=True)
    image = models.ImageField(_('obrázek'), upload_to=image_directory_path)
    price = models.PositiveIntegerField(_('cena za kurz'), null=False, blank=False)
    hours = models.PositiveIntegerField(_('počet hodin'), null=False, blank=False, validators=[MinValueValidator(1)])
    capacity = models.PositiveIntegerField(_('maximální kapacita'), null=True, blank=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL,
                                verbose_name='vedoucí', related_name='courses', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization,
                                     verbose_name='organizace', related_name='courses', on_delete=models.CASCADE)
    age_category = models.ForeignKey(AgeCategory,
                                     verbose_name='věková kategorie', related_name='courses', on_delete=models.CASCADE)
    topic = models.ManyToManyField(Topic, verbose_name='zaměření')
    status = models.CharField(_('stav'), max_length=9, choices=Status.choices, default=Status.DRAFT)
    date_from = models.DateTimeField(_('Datum začátku'), help_text='Kliknutím se otevře kalendář')
    date_to = models.DateTimeField(_('Datum konce'))
    week_schedule = models.ManyToManyField(WeekSchedule, verbose_name='týdenní rozvrh', blank=True)
    is_oneoff = models.BooleanField(_('Je jednodenní'), default=False)
    date_modified = models.DateTimeField(_('upraveno'), auto_now=True)
    date_created = models.DateTimeField(_('vytvořeno'), auto_now_add=True)
    objects = models.Manager()  # define implicitly to preserve this manager
    published = PublishedManager()

    class Meta:
        verbose_name = 'Aktivita'
        verbose_name_plural = 'Aktivity'

    def __str__(self):
        return f'{self.name} [{self.organization.name}]'

    def get_absolute_url(self):
        return reverse('course_detail', args=[self.slug])

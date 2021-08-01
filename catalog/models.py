from allauth.account.adapter import get_adapter
from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


class Organization(models.Model):
    name = models.CharField(_('název'), max_length=50, unique=True, blank=False)
    url = models.URLField(_('URL'), blank=False, help_text='např. https://vyberaktivitu.online')
    slug = models.SlugField(_('slug'), max_length=50)  # automated in views
    company_id = models.CharField(_('IČ'), max_length=8, blank=False)
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

    def get_absolute_url(self):
        return reverse('course_list_by_organization', args=(self.slug,))


class AgeCategory(models.Model):
    name = models.CharField(_('název'), max_length=30, blank=False)
    age_from = models.PositiveIntegerField(_('od věku'), blank=False)
    age_to = models.PositiveIntegerField(_('do věku'), blank=False)

    class Meta:
        verbose_name = 'Věková kategorie'
        verbose_name_plural = 'Věkové kategorie'

    def __str__(self):
        return f'{self.name} ({self.age_from}-{self.age_to})'


class WeekSchedule(models.Model):
    class WeekDay(models.IntegerChoices):
        MONDAY = 0, _('Pondělí')
        TUESDAY = 1, _('Úterý')
        WEDNESDAY = 2, _('Středa')
        THURSDAY = 3, _('Čtvrtek')
        FRIDAY = 4, _('Pátek')
        SATURDAY = 5, _('Sobota')
        SUNDAY = 6, _('Neděle')

    day_of_week = models.PositiveSmallIntegerField(validators=[MaxValueValidator(6)])  # 0-6
    hour = models.PositiveSmallIntegerField(validators=[MinValueValidator(7), MaxValueValidator(22)])  # 7-22

    class Meta:
        ordering = ['hour', 'day_of_week']
        verbose_name = 'Týdenní rozvrh'
        verbose_name_plural = 'Týdenní rozvrh'
        unique_together = [['day_of_week', 'hour']]

    def __str__(self):
        return f'{self.WeekDay.labels[self.day_of_week]} {str(self.hour).zfill(2)}:00'

    # helper function
    @classmethod
    def fill_table(cls):
        for i in range(7, 23):
            for j in range(7):
                cls.objects.create(day_of_week=j, hour=i)


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Course.Status.PUBLISHED)


def image_directory_path(instance, filename):
    return f'images/{instance.slug}.{filename.split(".")[-1]}'  # pathlib?


class Course(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Ke schválení')
        PUBLISHED = 'PUBLISHED', _('Publikováno')
        FINISHED = 'FINISHED', _('Ukončeno')

    class Category(models.TextChoices):
        OTHER = 'OTHER', _('Ostatní')
        LANG = 'LANG', _('Jazykové')
        MUSIC = 'MUSIC', _('Hudební')
        ART = 'ART', _('Umělecké')
        SPORT = 'SPORT', _('Sportovní')

    _original_status = None

    name = models.CharField(_('název'), max_length=50, blank=False)
    slug = AutoSlugField(_('slug'), populate_from='name', unique=True)
    description = models.TextField(_('popis'), blank=True)
    url = models.URLField(_('URL'), max_length=500, blank=True, help_text='např. https://vyberaktivitu.online')
    category = models.CharField(_('Kategorie'), max_length=5, choices=Category.choices, default=Category.OTHER)
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
    status = models.CharField(_('stav'), max_length=9, choices=Status.choices, default=Status.DRAFT)
    date_from = models.DateTimeField(_('Datum začátku'), help_text='Kliknutím se otevře kalendář')
    date_to = models.DateTimeField(_('Datum konce'))
    week_schedule = models.ManyToManyField(WeekSchedule, verbose_name='týdenní rozvrh', blank=True,
                                           related_name='courses')
    is_oneoff = models.BooleanField(_('Je jednodenní'), default=False)
    is_ad = models.BooleanField(_('Je topováno'), default=False)
    date_modified = models.DateTimeField(_('upraveno'), auto_now=True)
    date_created = models.DateTimeField(_('vytvořeno'), auto_now_add=True)
    objects = models.Manager()  # define implicitly to preserve this manager
    published = PublishedManager()
    tags = TaggableManager(help_text='oddělujte čárkami např.: angličtina, jazyk, doučování')

    class Meta:
        verbose_name = 'Aktivita'
        verbose_name_plural = 'Aktivity'
        ordering = ['-date_from']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status

    def __str__(self):
        return f'{self.name} [{self.organization.name}]'

    def save(self, *args, **kwargs):
        if self._original_status == self.Status.DRAFT and self.status == self.Status.PUBLISHED:
            self.send_notification_course_approved()
        super().save(*args, **kwargs)
        self._original_status = self.status

    def send_notification_course_approved(self):
        current_site = Site.objects.get_current()
        course_name = self.name
        get_adapter().send_mail('catalog/course/email/approved', self.teacher.email, {'course_name': course_name,
                                                                                      'current_site': current_site})

    def get_absolute_url(self):
        return reverse('course_detail', args=(self.slug,))

    def get_absolute_url_admin(self):  # for emails
        return reverse(f"admin:{self._meta.app_label}_{self._meta.model_name}_change", args=(self.id,))

    @classmethod
    def mark_finished(cls):
        update_queries = []
        for obj in cls.objects.filter(date_to__lt=timezone.now()):
            obj.status = cls.Status.FINISHED
            update_queries.append(obj)
        cls.objects.bulk_update(update_queries, ['status'])

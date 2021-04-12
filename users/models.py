from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from catalog.models import Organization


def photo_directory_path(instance, filename):
    email_slug = slugify(instance.email)
    return f'users/{email_slug}.{filename.split(".")[-1]}'  # pathlib?


class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff,
                          is_superuser=is_superuser,
                          **extra_fields
                          )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, **extra_fields)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        STUDENT = 'STUDENT', _('student')
        TEACHER = 'TEACHER', _('Vedoucí')
        COORDINATOR = 'COORDINATOR', _('Koordinátor')

    email = models.EmailField(_('emailová adresa'), max_length=40, unique=True)
    name = models.CharField(_('celé jméno'), max_length=30, blank=True)
    phone = models.CharField(_('telefonní číslo'), help_text='9 místné číslo bez předvolby', max_length=9, blank=True)
    role = models.CharField(max_length=30, choices=Roles.choices, default=Roles.STUDENT)  # another FK?
    organization = models.ForeignKey(Organization, verbose_name='organizace', null=True, related_name='users',
                                     on_delete=models.SET_NULL)
    photo = models.ImageField(_('fotografie'), help_text='minimální rozměr 200x200 px', upload_to=photo_directory_path,
                              blank=True)
    is_staff = models.BooleanField(_('správce'), default=False)
    is_superuser = models.BooleanField(_('supersprávce'), default=False)
    is_active = models.BooleanField(_('aktivní'), default=True)
    last_login = models.DateTimeField(_('poslední přihlášení'), null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Uživatel'
        verbose_name_plural = 'Uživatelé'

    def __str__(self):
        return f'{self.name or self.email}'


class StudentManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Roles.STUDENT)


class TeacherManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Roles.TEACHER)


class CoordinatorManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Roles.COORDINATOR)


class Student(User):
    objects = StudentManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = User.Roles.STUDENT
        return super().save(*args, **kwargs)


class Teacher(User):
    objects = TeacherManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = User.Roles.TEACHER
        return super().save(*args, **kwargs)


class Coordinator(User):
    objects = CoordinatorManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = User.Roles.COORDINATOR
        return super().save(*args, **kwargs)

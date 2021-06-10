from datetime import timedelta, datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase
from django.utils.text import slugify
from django.utils.timezone import make_aware, get_default_timezone

from catalog.models import Organization, Course, AgeCategory
from users.models import User


class OrganizationModelTests(TestCase):

    def setUp(self):
        self.name = 'Moje Organizace'
        self.slug = slugify(self.name)
        self.organization = Organization.objects.create(name=self.name,
                                                        slug=self.slug,
                                                        url='https://www.adresa.cz',
                                                        company_id=98765432,
                                                        address='Moje adresa 987',
                                                        town='Praha',
                                                        zip_code=77722)

    def test_str_dunder(self):
        self.assertEqual(str(self.organization), self.organization.name)

    def test_get_absolute_url(self):
        url = reverse('course_list_by_organization', args=(self.slug,))
        self.assertEqual(url, self.organization.get_absolute_url())


class AgeCategoryModelTests(TestCase):

    def setUp(self):
        self.age_category = AgeCategory.objects.create(name='Větší školáci',
                                                       age_from=11,
                                                       age_to=13)

    def test_str_dunder(self):
        text = f'{self.age_category.name} ({self.age_category.age_from}-{self.age_category.age_to})'
        self.assertEqual(str(self.age_category), text)


class CourseModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='lofy@seznam.cz', password='heslo123')
        self.organization = Organization.objects.create(name='Moje Organizace',
                                                        slug='moje-organizace',
                                                        url='https://www.adresa.cz',
                                                        company_id=98765432,
                                                        address='Moje adresa 987',
                                                        town='Praha',
                                                        zip_code=77722)
        self.age_category = AgeCategory.objects.create(name='Větší školáci',
                                                       age_from=11,
                                                       age_to=13)
        timezone = get_default_timezone()
        self.course = Course.objects.create(
            name='Název aktivity',
            url='https://www.organizace.cz/aktivita',
            tags='pokus-tag',
            category=Course.Category.OTHER,  # predefined in Course model
            description='Mǔj popis pravidelné aktivity.',
            image=SimpleUploadedFile(name='test_image_new.jpg',
                                     content=open('static/img/test_image.jpg',
                                                  'rb').read(),
                                     content_type='image/jpeg'),
            price=2000,
            hours=100,
            capacity=10,
            teacher=self.user,
            age_category=self.age_category,  # use first
            date_from=make_aware(datetime.today() + timedelta(days=1), timezone=timezone),
            date_to=make_aware(datetime.today() + timedelta(days=2), timezone=timezone),
            organization=self.organization
        )

    def test_str_dunder(self):
        text = f'{self.course.name} [{self.organization.name}]'
        self.assertEqual(str(self.course), text)

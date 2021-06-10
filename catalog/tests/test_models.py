from django.test import TestCase, override_settings
from catalog.models import Organization, Course, AgeCategory
from django.utils.text import slugify
from django.shortcuts import reverse


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

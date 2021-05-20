from django.shortcuts import reverse
from django.test import SimpleTestCase
from django.urls import resolve

from catalog.views import (home, dashboard, search, course_detail, course_list, about_us, cooperation, conditions, gdpr, \
                           course_list_by_organization, course_create, oneoff_course_create, course_update,
                           oneoff_course_update, course_delete, organization_register, organization_update,
                           organization_rename, organization_delete)


class TestURLs(SimpleTestCase):

    def test_root_url_resolves(self):
        url = reverse('home')
        self.assertEqual(resolve(url).func, home)

    def test_dashboard_url_resolves(self):
        url = reverse('dashboard')
        self.assertEqual(resolve(url).func, dashboard)

    def test_search_url_resolves(self):
        url = reverse('search')
        self.assertEqual(resolve(url).func, search)

    def test_course_list_url_resolves(self):
        url = reverse('course_list')
        self.assertEqual(resolve(url).func, course_list)

    def test_course_list_by_organization_url_resolves(self):
        url = reverse('course_list_by_organization', args=('some-organization-slug',))
        self.assertEqual(resolve(url).func, course_list_by_organization)

    def test_cooperation_url_resolves(self):
        url = reverse('cooperation')
        self.assertEqual(resolve(url).func, cooperation)

    def test_about_us_url_resolves(self):
        url = reverse('about_us')
        self.assertEqual(resolve(url).func, about_us)

    def test_gdpr_url_resolves(self):
        url = reverse('gdpr')
        self.assertEqual(resolve(url).func, gdpr)

    def test_conditions_url_resolves(self):
        url = reverse('conditions')
        self.assertEqual(resolve(url).func, conditions)

    # course create/read/update/delete
    def test_detail_url_resolves(self):
        url = reverse('course_detail', args=('some-course-slug',))
        self.assertEqual(resolve(url).func, course_detail)

    def test_course_create_url_resolves(self):
        url = reverse('course_create')
        self.assertEqual(resolve(url).func, course_create)

    def test_oneoff_course_create_url_resolves(self):
        url = reverse('oneoff_course_create')
        self.assertEqual(resolve(url).func, oneoff_course_create)

    def test_course_update_url_resolves(self):
        url = reverse('course_update', args=('some-course-slug',))
        self.assertEqual(resolve(url).func, course_update)

    def test_oneoff_course_update_url_resolves(self):
        url = reverse('oneoff_course_update', args=('some-course-slug',))
        self.assertEqual(resolve(url).func, oneoff_course_update)

    def test_course_delete_url_resolves(self):
        url = reverse('course_delete', args=('some-course-slug',))
        self.assertEqual(resolve(url).func, course_delete)

    # organization create/update/delete
    def test_organization_create_url_resolves(self):
        url = reverse('organization_register')
        self.assertEqual(resolve(url).func, organization_register)

    def test_organization_update_url_resolves(self):
        url = reverse('organization_update')
        self.assertEqual(resolve(url).func, organization_update)

    def test_organization_rename_url_resolves(self):
        url = reverse('organization_rename')
        self.assertEqual(resolve(url).func, organization_rename)

    def test_organization_delete_url_resolves(self):
        url = reverse('organization_delete')
        self.assertEqual(resolve(url).func, organization_delete)

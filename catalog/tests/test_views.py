from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from django.utils.text import slugify

from catalog.models import Organization
from users.models import User


# class ListViews(TestCase):
#
#     def setUp(self) -> None:
#         self.new_user = User.objects.create_user(email='lofy@seznam.cz', password='heslo123')
#         self.new_organization = Organization.objects.create(name='Moje Organizace',
#                                                             url='https://www.adresa.cz',
#                                                             company_id=98765432,
#                                                             address='Moje adresa 987',
#                                                             town='Praha',
#                                                             zip_code=77722)
#         self.age_category = AgeCategory.objects.create(name='Větší školáci',
#                                                        age_from=11,
#                                                        age_to=13)
#         WeekSchedule.fill_table()
#         # TODO: price, hours, capacity, teacher, organization, age_category,
#         # TODO: status,
#         self.new_course = Course.objects.create(name='Moje aktivita',
#                                                 description='Mǔj popis aktivity',
#                                                 url='https://www.adresa-aktivity.cz',
#                                                 category=Course.Category.OTHER,
#                                                 image=SimpleUploadedFile(name='test_image_new.jpg',
#                                                                          content=open('static/img/test_image.jpg',
#                                                                                       'rb').read(),
#                                                                          content_type='image/jpeg'),
#                                                 price=2000,
#                                                 hours=100,
#                                                 capacity=10,
#                                                 teacher=self.new_user,
#                                                 organization=self.new_organization,
#                                                 age_category=self.age_category,
#                                                 status=Course.Status.PUBLISHED,
#                                                 date_from=datetime.now() + timedelta(days=1),
#                                                 date_to=datetime.now() + timedelta(days=2),
#                                                 )
#
#         self.new_course2 = Course.objects.create(name='Moje další aktivita',
#                                                  description='Mǔj další popis aktivity',
#                                                  url='https://www.adresa-aktivity.cz',
#                                                  category=Course.Category.OTHER,
#                                                  image=SimpleUploadedFile(name='test_image_new2.jpg',
#                                                                           content=open('static/img/test_image.jpg',
#                                                                                        'rb').read(),
#                                                                           content_type='image/jpeg'),
#                                                  price=2000,
#                                                  hours=100,
#                                                  capacity=10,
#                                                  teacher=self.new_user,
#                                                  organization=self.new_organization,
#                                                  age_category=self.age_category,
#                                                  status=Course.Status.PUBLISHED,
#                                                  date_from=datetime.now() + timedelta(days=1),
#                                                  date_to=datetime.now() + timedelta(days=2),
#                                                  )

# def test_search_GET(self):
#     self.new_organization.slug = slugify(self.new_organization.name)
#     self.new_organization.save()
#     response = self.client.get(reverse('search'))
#     self.assertEqual(response.status_code, 200)
#     self.assertTemplateUsed(response, 'catalog/course/search.html')
#
# def test_course_list_GET(self):
#     response = self.client.get(reverse('course_list'))
#     self.assertEqual(response.status_code, 200)
#     self.assertTemplateUsed(response, 'catalog/course/list.html')
#
# def test_course_list_by_organization_GET(self):
#     url = reverse('course_list_by_organization', args=('some-org',))
#     response = self.client.get(url)
#     self.assertEqual(response.status_code, 200)
#     self.assertTemplateUsed(response, 'catalog/course/list_organization.html')


class OrganizationTests(TestCase):
    data = {'name': 'Nová organizace',
            'url': 'https://www.nova-organizace.cz',
            'company_id': 98765443,
            'address': 'Moje adresa 123',
            'town': 'Praha',
            'zip_code': 33322}

    def setUp(self) -> None:
        self.new_user = User.objects.create_user(email='lofy@seznam.cz', password='heslo123')
        self.client.login(email='lofy@seznam.cz', password='heslo123')

    def test_organization_register_uses_correct_template_GET(self):
        url = reverse('organization_register')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/organization/register.html')

    def test_organization_update_uses_correct_template_GET(self):
        url = reverse('organization_register')
        self.client.post(url, self.data)
        self.new_user.refresh_from_db()  # necessary because of "request.user" modifications

        url2 = reverse('organization_update')
        response = self.client.get(url2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/organization/update.html')

    def test_organization_rename_uses_correct_template_GET(self):
        url = reverse('organization_register')
        self.client.post(url, self.data)
        self.new_user.refresh_from_db()  # necessary because of "request.user" modifications

        url2 = reverse('organization_rename')
        response = self.client.get(url2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/organization/rename.html')

    def test_organization_delete_uses_correct_template_GET(self):
        url = reverse('organization_register')
        self.client.post(url, self.data)
        self.new_user.refresh_from_db()  # necessary because of "request.user" modifications

        url2 = reverse('organization_delete')
        response = self.client.get(url2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/organization/delete.html')

    # registering
    def test_organization_register_redirects_and_saves_data_to_db_POST(self):
        url = reverse('organization_register')

        response = self.client.post(url, self.data)

        self.assertEquals(response.status_code, 302)
        self.assertEqual(Organization.objects.count(), 1)

    def test_organization_register_creates_slug_from_name_POST(self):
        url = reverse('organization_register')

        self.client.post(url, self.data)

        new_organization = Organization.objects.first()
        self.assertEqual(new_organization.slug, slugify(new_organization.name))

    def test_organization_register_modifies_users_role_and_organization_POST(self):
        url = reverse('organization_register')

        self.client.post(url, self.data)

        new_organization = Organization.objects.first()
        self.new_user.refresh_from_db()  # necessary because of "request.user" modifications
        self.assertEquals(self.new_user.role, User.Roles.COORDINATOR)
        self.assertEquals(self.new_user.organization, new_organization)

    # updating
    def test_organization_update_uses_users_organization_GET(self):
        url = reverse('organization_register')
        self.client.post(url, self.data)
        self.new_user.refresh_from_db()  # necessary because of "request.user" modifications

        url2 = reverse('organization_update')
        response = self.client.get(url2)

        self.assertEqual(self.new_user.organization, response.context['user_organization'])

    # renaming
    def test_organization_rename_uses_users_organization_GET(self):
        url = reverse('organization_register')
        self.client.post(url, self.data)
        self.new_user.refresh_from_db()  # necessary because of "request.user" modifications

        url2 = reverse('organization_rename')
        response = self.client.get(url2)

        self.assertEqual(self.new_user.organization, response.context['user_organization'])

    def test_organization_rename_redirects_and_modifies_current_slug_POST(self):
        url = reverse('organization_register')
        self.client.post(url, self.data)
        self.new_user.refresh_from_db()  # necessary because of "request.user" modifications

        url2 = reverse('organization_rename')
        response = self.client.post(url2, {'name': 'Přejmenovaná organizace'})

        new_organization = Organization.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(new_organization.slug, slugify(new_organization.name))

    # deleting
    def test_organization_delete_uses_users_organization_GET(self):
        url = reverse('organization_register')
        self.client.post(url, self.data)
        self.new_user.refresh_from_db()  # necessary because of "request.user" modifications

        url2 = reverse('organization_delete')
        response = self.client.get(url2)

        self.assertEqual(self.new_user.organization, response.context['user_organization'])

    def test_organization_delete_removes_organization_POST(self):
        url = reverse('organization_register')
        self.client.post(url, self.data)
        self.new_user.refresh_from_db()  # necessary because of "request.user" modifications

        url2 = reverse('organization_delete')
        self.client.post(url2)

        self.assertEqual(Organization.objects.count(), 0)

    def test_organization_delete_modifies_users_role_POST(self):
        url = reverse('organization_register')
        self.client.post(url, self.data)

        url2 = reverse('organization_delete')
        self.client.post(url2)
        self.new_user.refresh_from_db()  # necessary because of "request.user" modifications

        self.assertEquals(self.new_user.role, User.Roles.STUDENT)


class StaticPagesTests(SimpleTestCase):

    def test_home_GET(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/home.html')

    def test_gdpr_GET(self):
        response = self.client.get(reverse('gdpr'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/gdpr.html')

    def test_conditions_GET(self):
        response = self.client.get(reverse('conditions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/conditions.html')

    def test_cooperation_GET(self):
        response = self.client.get(reverse('cooperation'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/cooperation.html')

    def test_about_GET(self):
        response = self.client.get(reverse('about_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/about.html')

# class CourseTests(TestCase):
#
#     def test_detail_GET(self):
#         url = self.new_course.get_absolute_url()
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'catalog/course/detail.html')

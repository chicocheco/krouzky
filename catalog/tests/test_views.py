import shutil
from datetime import timedelta, date

from PIL import Image
from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.forms.models import model_to_dict
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.text import slugify

from catalog.models import Organization, Course, AgeCategory
from users.models import User

TEST_DIR = settings.BASE_DIR / 'test_data'


class StaticPagesTests(TestCase):

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


class OrganizationTests(TestCase):

    def setUp(self):
        self.new_user = User.objects.create_user(email='lofy@seznam.cz', password='heslo123')
        self.client.login(email='lofy@seznam.cz', password='heslo123')
        self.data = {'name': 'Nová organizace',
                     'url': 'https://www.nova-organizace.cz',
                     'company_id': 98765443,
                     'address': 'Moje adresa 123',
                     'town': 'Praha',
                     'zip_code': 33322}

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

        self.assertEqual(response.status_code, 302)
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
        self.assertEqual(self.new_user.role, User.Roles.COORDINATOR)
        self.assertEqual(self.new_user.organization, new_organization)

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

        self.assertEqual(self.new_user.role, User.Roles.STUDENT)


@override_settings(MEDIA_ROOT=(TEST_DIR / 'media'))
class CourseTests(TestCase):

    def setUp(self):
        call_command('flush', '--no-input')  # else it does clear db between tests
        self.new_user = User.objects.create_user(email='lofy@seznam.cz', password='heslo123')
        self.client.login(email='lofy@seznam.cz', password='heslo123')
        # do what organization_register view does here:
        organization_name = 'Moje Organizace'
        self.new_organization = Organization.objects.create(name=organization_name,
                                                            slug=slugify(organization_name),
                                                            url='https://www.adresa.cz',
                                                            company_id=98765432,
                                                            address='Moje adresa 987',
                                                            town='Praha',
                                                            zip_code=77722)
        self.new_user.organization = self.new_organization
        self.new_user.role = User.Roles.COORDINATOR
        self.new_user.save()

        self.age_category = AgeCategory.objects.create(name='Větší školáci',
                                                       age_from=11,
                                                       age_to=13)

        self.data_regular = {
            'name': 'Název pravidelné SUPER aktivity',
            'url': 'https://www.organizace.cz/pravidelna-aktivita',
            'tags': 'pokus-tag',
            'category': 'OTHER',  # predefined in Course model
            'description': 'Mǔj popis pravidelné aktivity.',
            'image': SimpleUploadedFile(name='test_image_new.jpg',
                                        content=open('static/img/test_image.jpg',
                                                     'rb').read(),
                                        content_type='image/jpeg'),
            'price': 2000,
            'hours': 100,
            'capacity': 10,
            'teacher': 1,  # use first
            'age_category': 1,  # use first
            'date_from': date.today() + timedelta(days=1),
            'date_to': date.today() + timedelta(days=2),
        }

        self.data_oneoff = {
            'name': 'Název jednodenní SUPER aktivity',
            'url': 'https://www.organizace.cz/jednodenni-aktivita',
            'tags': 'pokus-tag',
            'category': 'OTHER',  # predefined in Course model
            'description': 'Mǔj popis jednodenní aktivity.',
            'image': SimpleUploadedFile(name='test_image_new.jpg',
                                        content=open('static/img/test_image.jpg',
                                                     'rb').read(),
                                        content_type='image/jpeg'),
            'price': 2000,
            'hours': 100,
            'capacity': 10,
            'teacher': 1,  # use first
            'age_category': 1,  # use first
            'date_from': date.today() + timedelta(days=1),
            'date_to': date.today() + timedelta(days=1),  # same day
            'time_from': '14:00',
            'time_to': '16:00',

        }

    @classmethod
    def tearDownClass(cls):
        print(f'\nDeleting temporary files from {TEST_DIR}...\n')
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass

    def create_published_course(self):
        url = reverse('course_create')
        response = self.client.post(url, self.data_regular)
        course = Course.objects.first()
        course.status = Course.Status.PUBLISHED  # as if approved by admins
        course.save()
        return course, response

    def create_published_oneoff_course(self):
        url = reverse('oneoff_course_create')
        response = self.client.post(url, self.data_oneoff)
        course = Course.objects.first()
        course.status = Course.Status.PUBLISHED  # as if approved by admins
        course.save()
        return course, response

    def create_draft_course(self):
        url = reverse('course_create')
        response = self.client.post(url, self.data_regular)
        return Course.objects.first(), response

    def create_draft_oneoff_course(self):
        url = reverse('oneoff_course_create')
        response = self.client.post(url, self.data_oneoff)
        return Course.objects.first(), response

    def test_course_create_uses_correct_template_GET(self):
        url = reverse('course_create')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/course/create.html')

    def test_oneoff_course_create_uses_correct_template_GET(self):
        url = reverse('oneoff_course_create')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/course/create_oneoff.html')

    def test_course_create_creates_new_object_POST(self):
        url = reverse('course_create')

        self.client.post(url, self.data_regular)

        self.assertEqual(Course.objects.count(), 1)

    def test_oneoff_course_create_creates_new_object_POST(self):
        url = reverse('oneoff_course_create')

        self.client.post(url, self.data_oneoff)

        self.assertEqual(Course.objects.count(), 1)

    def test_course_create_get_assigned_users_organization_POST(self):
        course, response = self.create_draft_course()

        self.assertEqual(course.organization, self.new_organization)

    def test_oneoff_course_create_get_assigned_users_organization_POST(self):
        course, response = self.create_draft_oneoff_course()

        self.assertEqual(course.organization, self.new_organization)

    def test_course_create_capitalizes_name_POST(self):
        course, response = self.create_draft_course()

        self.assertEqual(course.name, self.data_regular['name'].capitalize())

    def test_oneoff_course_create_capitalizes_name_POST(self):
        course, response = self.create_draft_oneoff_course()

        self.assertEqual(course.name, self.data_oneoff['name'].capitalize())

    def test_course_create_resizes_uploaded_image_POST(self):
        course, response = self.create_draft_course()

        with open(course.image.path, 'rb') as fp:
            image = Image.open(fp)
        self.assertEqual(image.size, (settings.SIDE_LENGTH_COURSE_IMG, settings.SIDE_LENGTH_COURSE_IMG))

    def test_oneoff_course_create_resizes_uploaded_image_POST(self):
        course, response = self.create_draft_oneoff_course()

        with open(course.image.path, 'rb') as fp:
            image = Image.open(fp)
        self.assertEqual(image.size, (settings.SIDE_LENGTH_COURSE_IMG, settings.SIDE_LENGTH_COURSE_IMG))

    def test_course_create_sends_correct_email_about_pending_approval_POST(self):
        course, response = self.create_draft_course()

        course_url_admin = course.get_absolute_url_admin()
        self.assertIn(course_url_admin, mail.outbox[0].body)

    def test_oneoff_course_create_sends_correct_email_about_pending_approval_POST(self):
        course, response = self.create_draft_oneoff_course()

        course_url_admin = course.get_absolute_url_admin()
        self.assertIn(course_url_admin, mail.outbox[0].body)

    def test_course_create_redirects_to_detail_POST(self):
        course, response = self.create_draft_course()

        self.assertEqual(response.url, course.get_absolute_url())

    def test_oneoff_course_create_redirects_to_detail_POST(self):
        course, response = self.create_draft_oneoff_course()

        self.assertEqual(response.url, course.get_absolute_url())

    def test_course_update_updating_name_changes_status_to_draft_POST(self):
        course, response = self.create_published_course()

        url2 = reverse('course_update', args=(course.slug,))  # switches to DRAFT?
        new_name = 'Modifikovaný název'
        modified_data = model_to_dict(course)
        modified_data['name'] = new_name
        self.client.post(url2, modified_data)
        course_modified = Course.objects.first()

        self.assertEqual(course.id, course_modified.id)
        self.assertEqual(course_modified.status, Course.Status.DRAFT.value)
        self.assertEqual(course_modified.name, new_name)

    def test_course_update_updating_description_changes_status_to_draft_POST(self):
        course, response = self.create_published_course()

        url2 = reverse('course_update', args=(course.slug,))  # switches to DRAFT?
        new_description = 'Modifikovaný popisek aktivity.'
        modified_data = model_to_dict(course)
        modified_data['description'] = new_description
        self.client.post(url2, modified_data)
        course_modified = Course.objects.first()
        course_url_admin = course_modified.get_absolute_url_admin()

        self.assertEqual(course.id, course_modified.id)
        self.assertEqual(course_modified.status, Course.Status.DRAFT.value)
        self.assertEqual(course_modified.description, new_description)
        self.assertIn(course_url_admin, mail.outbox[0].body)

    def test_course_update_updating_description_sends_correct_email_about_pending_reapproval_POST(self):
        course, response = self.create_published_course()
        url2 = reverse('course_update', args=(course.slug,))  # switches to DRAFT?

        new_description = 'Modifikovaný popisek aktivity.'
        modified_data = model_to_dict(course)
        modified_data['description'] = new_description
        self.client.post(url2, modified_data)
        course_modified = Course.objects.first()
        course_url_admin = course_modified.get_absolute_url_admin()

        self.assertIn(course_url_admin, mail.outbox[0].body)

    def test_course_update_updating_price_field_does_not_change_status_POST(self):
        course, response = self.create_published_course()

        url2 = reverse('course_update', args=(course.slug,))  # switches to DRAFT?
        new_price = 500
        modified_data = model_to_dict(course)
        modified_data['price'] = new_price
        self.client.post(url2, modified_data)
        course_modified = Course.objects.first()

        self.assertEqual(course.id, course_modified.id)
        self.assertEqual(course_modified.status, course.status)
        self.assertEqual(course_modified.price, new_price)

    def test_course_detail_GET(self):
        course, response = self.create_published_course()

        response = self.client.get(reverse('course_detail', args=(course.slug,)))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/course/detail.html')

    def test_course_detail_not_found_GET(self):
        response = self.client.get(reverse('course_detail', args=('non-existent',)))

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_course_delete_POST(self):
        course, response = self.create_published_course()

        self.client.post(reverse('course_delete', args=(course.slug,)))
        self.assertEqual(Course.objects.count(), 0)

    def test_course_detail_cannot_access_someone_elses_draft(self):
        course, response = self.create_draft_course()
        self.client.logout()
        self.other_user = User.objects.create_user(email='other@gmail.com', password='heslo123')
        self.client.login(email='other@gmail.com', password='heslo123')
        url = reverse('course_detail', args=(course.slug,))  # switches to DRAFT?

        response = self.client.get(url)

        self.assertInHTML('Přístup odepřen', response.content.decode())
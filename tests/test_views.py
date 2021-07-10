import shutil
from datetime import timedelta, date, time

from PIL import Image
from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.forms.models import model_to_dict
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import localtime

from catalog.models import Organization, Course, AgeCategory
from invitations.models import Invitation
from users.models import User

TEST_DIR = settings.BASE_DIR / 'test_data'
USERNAME = 'uzivatel@seznam.cz'
OTHER_USERNAME = 'jiny_uzivatel@seznam.cz'
INVITED_USERNAME = 'pozvany@seznam.cz'
PASSWORD = 'heslo123'


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
        self.user = User.objects.create_user(email=USERNAME, password=PASSWORD)
        self.client.login(email=USERNAME, password=PASSWORD)
        self.data = {'name': 'Nová organizace',
                     'url': 'https://www.nova-organizace.cz',
                     'company_id': 98765443,
                     'address': 'Moje adresa 123',
                     'town': 'Praha',
                     'zip_code': 33322}

    def register_organization(self):
        url = reverse('organization_register')
        self.client.post(url, self.data)
        self.user.refresh_from_db()  # necessary because of "request.user" modifications
        return Organization.objects.first()

    def invite_logged_in_teacher(self):
        input_data = {'invited_email': USERNAME}
        self.client.post(reverse('organization_invite_teacher'), data=input_data)
        invitation = Invitation.objects.last()
        invite_url = reverse('accept_invite_teacher', args=(invitation.key,))
        return input_data, invite_url

    def invite_teacher(self):
        input_data = {'invited_email': INVITED_USERNAME}
        self.client.post(reverse('organization_invite_teacher'), data=input_data)
        invitation = Invitation.objects.last()
        invite_url = reverse('accept_invite_teacher', args=(invitation.key,))
        return input_data, invite_url

    def test_organization_register_uses_correct_template_GET(self):
        url = reverse('organization_register')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/organization/register.html')

    def test_organization_update_uses_correct_template_GET(self):
        self.register_organization()

        url2 = reverse('organization_update')
        response = self.client.get(url2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/organization/update.html')

    def test_organization_rename_uses_correct_template_GET(self):
        self.register_organization()

        url2 = reverse('organization_rename')
        response = self.client.get(url2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/organization/rename.html')

    def test_organization_delete_uses_correct_template_GET(self):
        self.register_organization()

        url2 = reverse('organization_delete')
        response = self.client.get(url2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/organization/delete.html')

    def test_organization_members_uses_correct_template_GET(self):
        self.register_organization()

        response = self.client.get(reverse('organization_members'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/organization/members.html')

    def test_organization_remove_member_uses_correct_template_GET(self):
        organization = self.register_organization()
        other_user = User.objects.create_user(email=OTHER_USERNAME, password=PASSWORD)
        other_user.organization = organization
        other_user.role = User.Roles.TEACHER
        other_user.save()

        response = self.client.get(reverse('organization_remove_member', args=(other_user.pk,)))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/organization/remove_member.html')

    def test_AcceptInviteTeacher_uses_correct_template_GET(self):
        self.register_organization()
        _, invite_url = self.invite_teacher()

        response = self.client.get(invite_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invitations/accept_invite_teacher.html')

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
        self.user.refresh_from_db()  # necessary because of "request.user" modifications
        self.assertEqual(self.user.role, User.Roles.COORDINATOR)
        self.assertEqual(self.user.organization, new_organization)

    # updating
    def test_organization_update_uses_users_organization_GET(self):
        self.register_organization()

        url2 = reverse('organization_update')
        response = self.client.get(url2)

        self.assertEqual(self.user.organization, response.context['user_organization'])

    def test_organization_update_cannot_be_accessed_by_teacher_GET(self):
        self.register_organization()
        self.user.role = User.Roles.TEACHER
        self.user.save()

        response = self.client.get(reverse('organization_update'))

        self.assertInHTML('Přístup odepřen', response.content.decode())

    # renaming
    def test_organization_rename_uses_users_organization_GET(self):
        self.register_organization()

        url2 = reverse('organization_rename')
        response = self.client.get(url2)

        self.assertEqual(self.user.organization, response.context['user_organization'])

    def test_organization_rename_redirects_and_modifies_current_slug_POST(self):
        self.register_organization()

        url2 = reverse('organization_rename')
        response = self.client.post(url2, {'name': 'Přejmenovaná organizace'})

        new_organization = Organization.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(new_organization.slug, slugify(new_organization.name))

    def test_organization_rename_cannot_be_accessed_by_teacher_GET(self):
        self.register_organization()
        self.user.role = User.Roles.TEACHER
        self.user.save()

        response = self.client.get(reverse('organization_rename'))

        self.assertInHTML('Přístup odepřen', response.content.decode())

    # deleting
    def test_organization_delete_uses_users_organization_GET(self):
        self.register_organization()

        url2 = reverse('organization_delete')
        response = self.client.get(url2)

        self.assertEqual(self.user.organization, response.context['user_organization'])

    def test_organization_delete_removes_organization_POST(self):
        self.register_organization()

        url2 = reverse('organization_delete')
        self.client.post(url2)

        self.assertEqual(Organization.objects.count(), 0)

    def test_organization_delete_modifies_users_role_POST(self):
        self.register_organization()

        url2 = reverse('organization_delete')
        self.client.post(url2)
        self.user.refresh_from_db()  # necessary because of "request.user" modifications

        self.assertEqual(self.user.role, User.Roles.STUDENT)

    def test_organization_delete_cannot_be_accessed_by_teacher_GET(self):
        self.register_organization()
        self.user.role = User.Roles.TEACHER
        self.user.save()

        response = self.client.get(reverse('organization_delete'))

        self.assertInHTML('Přístup odepřen', response.content.decode())

    # members
    def test_organization_members_cannot_be_accessed_by_teacher_GET(self):
        self.register_organization()
        self.user.role = User.Roles.TEACHER
        self.user.save()

        response = self.client.get(reverse('organization_members'))

        self.assertInHTML('Přístup odepřen', response.content.decode())

    def test_organization_members_lists_teachers_organization_GET(self):
        organization = self.register_organization()
        other_user = User.objects.create_user(email=OTHER_USERNAME, password=PASSWORD)
        other_user.organization = organization
        other_user.role = User.Roles.TEACHER
        other_user.save()

        response = self.client.get(reverse('organization_members'))

        self.assertInHTML(other_user.email, response.content.decode())

    def test_organization_remove_member_POST(self):
        organization = self.register_organization()
        other_user = User.objects.create_user(email=OTHER_USERNAME, password=PASSWORD)
        other_user.organization = organization
        other_user.role = User.Roles.TEACHER
        other_user.save()

        self.client.post(reverse('organization_remove_member', args=(other_user.pk,)))
        other_user.refresh_from_db()

        self.assertIsNone(other_user.organization)
        self.assertEqual(other_user.role, User.Roles.STUDENT)

    def test_organization_remove_member_cannot_remove_users_that_do_not_belong_to_users_organization_POST(self):
        self.register_organization()
        other_user = User.objects.create_user(email=OTHER_USERNAME, password=PASSWORD)  # no org. assigned
        other_user.save()

        response = self.client.post(reverse('organization_remove_member', args=(other_user.pk,)))
        other_user.refresh_from_db()

        self.assertInHTML('Přístup odepřen', response.content.decode())

    def test_organization_remove_member_current_user_cannot_remove_themselves_POST(self):
        self.register_organization()

        response = self.client.post(reverse('organization_remove_member', args=(self.user.pk,)))
        self.user.refresh_from_db()

        self.assertInHTML('Přístup odepřen', response.content.decode())

    def test_organization_remove_member_cannot_be_accessed_by_teacher_GET(self):
        organization = self.register_organization()
        self.user.role = User.Roles.TEACHER
        self.user.save()
        other_user = User.objects.create_user(email=OTHER_USERNAME, password=PASSWORD)
        other_user.organization = organization
        other_user.role = User.Roles.TEACHER
        other_user.save()

        response = self.client.get(reverse('organization_remove_member', args=(other_user.pk,)))

        self.assertInHTML('Přístup odepřen', response.content.decode())

    # leaving
    def test_organization_leave_unassigns_organization_and_changes_status_to_student_POST(self):
        self.register_organization()
        self.user.role = User.Roles.TEACHER
        self.user.save()

        self.client.post(reverse('organization_leave'))
        self.user.refresh_from_db()

        self.assertEqual(self.user.role, User.Roles.STUDENT)
        self.assertEqual(self.user.organization, None)

    def test_organization_leave_can_be_accessed_only_by_teacher_GET(self):
        self.register_organization()
        response = self.client.get(reverse('organization_leave'))  # as coordinator

        self.assertInHTML('Přístup odepřen', response.content.decode())

    # inviting
    def test_organization_invite_teacher_sends_invitation_POST(self):
        self.register_organization()
        input_data, _ = self.invite_teacher()

        self.assertIn(f"Vaše e-mailová adresa ({input_data['invited_email']}) byla použita v pozvánce",
                      mail.outbox[-1].body)

    def test_organization_invite_teacher_cannot_be_accessed_by_teacher_GET(self):
        self.register_organization()
        self.user.role = User.Roles.TEACHER
        self.user.save()

        response = self.client.get(reverse('organization_invite_teacher'))

        self.assertInHTML('Přístup odepřen', response.content.decode())

    # invitations app
    def test_AcceptInviteTeacher_logs_out_user_if_is_not_the_invited_one_GET(self):
        self.register_organization()
        _, invite_url = self.invite_teacher()

        response = self.client.get(invite_url)
        logout_message = str(list(response.context['messages'])[-1])

        self.assertEqual(logout_message, 'Právě jste byl odhlášen.')

    def test_AcceptInviteTeacher_renders_correct_variables_in_HTML_GET(self):
        self.register_organization()
        input_data, invite_url = self.invite_teacher()

        response = self.client.get(invite_url)

        self.assertInHTML(f'Přejete si přijmout pozvánku do organizace <b>{self.data["name"]}</b> '
                          f'pro <b>{input_data["invited_email"]}</b>?', response.content.decode())

    def test_AcceptInviteTeacher_redirects_nonexisting_user_to_signup_page_POST(self):
        self.register_organization()
        _, invite_url = self.invite_teacher()

        response = self.client.post(invite_url)

        self.assertEqual(response.url, reverse('account_signup'))

    # TODO: test whether non-existing user accepted the invitation after signing up
    # def test_AcceptInviteTeacher_accepts_invitation_of_after_signing_up_POST(self):

    def test_AcceptInviteTeacher_accepts_invitation_of_logged_in_user_POST(self):
        self.register_organization()
        _, invite_url = self.invite_logged_in_teacher()

        self.client.post(invite_url)
        invitation = Invitation.objects.last()

        self.assertTrue(invitation.is_accepted)

    def test_AcceptInviteTeacher_redirects_logged_in_user_to_dashboard_page_POST(self):
        self.register_organization()
        _, invite_url = self.invite_logged_in_teacher()

        response = self.client.post(invite_url)

        self.assertEqual(response.url, reverse('dashboard'))

    def test_AcceptInviteTeacher_redirects_existing_logged_out_user_to_invited_account_login_page_POST(self):
        self.register_organization()
        _, invite_url = self.invite_logged_in_teacher()

        self.client.logout()
        response = self.client.post(invite_url)

        self.assertEqual(response.url, reverse('invited_account_login'))

    def test_AcceptInviteTeacher_existing_logged_out_user_accepts_invitation_POST(self):
        self.register_organization()
        input_data, invite_url = self.invite_logged_in_teacher()

        self.client.logout()
        self.client.post(invite_url)
        # login-page, invitation accepted...
        invitation = Invitation.objects.get(invited_email=input_data['invited_email'])

        self.assertTrue(invitation.is_accepted)

    def test_AcceptInviteTeacher_existing_logged_out_user_accepts_only_after_sending_post_request_POST(self):
        self.register_organization()
        input_data, invite_url = self.invite_logged_in_teacher()

        invitation = Invitation.objects.get(invited_email=input_data['invited_email'])

        self.assertFalse(invitation.is_accepted)


@override_settings(MEDIA_ROOT=(TEST_DIR / 'media'))
class CourseTests(TestCase):

    def setUp(self):
        call_command('flush', '--no-input')  # else it does clear db between tests
        self.user = User.objects.create_user(email=USERNAME, password=PASSWORD)
        self.client.login(email=USERNAME, password=PASSWORD)
        # do what organization_register view does here:
        organization_name = 'Moje Organizace'
        self.new_organization = Organization.objects.create(name=organization_name,
                                                            slug=slugify(organization_name),
                                                            url='https://www.adresa.cz',
                                                            company_id=98765432,
                                                            address='Moje adresa 987',
                                                            town='Praha',
                                                            zip_code=77722)
        self.user.organization = self.new_organization
        self.user.role = User.Roles.COORDINATOR
        self.user.save()

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
            'time_from': time(12, 0),
            'time_to': time(14, 0),
        }

    @classmethod
    def tearDownClass(cls):
        print(f'\nDeleting temporary files from {TEST_DIR}...\n')
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass

    # helpers
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

    # START OF CREATE VIEWS
    # create object
    def test_course_create_creates_new_object_POST(self):
        url = reverse('course_create')

        self.client.post(url, self.data_regular)

        self.assertEqual(Course.objects.count(), 1)

    def test_oneoff_course_create_creates_new_object_POST(self):
        url = reverse('oneoff_course_create')

        self.client.post(url, self.data_oneoff)

        self.assertEqual(Course.objects.count(), 1)

    # assign organization
    def test_course_create_get_assigned_users_organization_POST(self):
        course, response = self.create_draft_course()

        self.assertEqual(course.organization, self.new_organization)

    def test_oneoff_course_create_get_assigned_users_organization_POST(self):
        course, response = self.create_draft_oneoff_course()

        self.assertEqual(course.organization, self.new_organization)

    # capitalize name
    def test_course_create_capitalizes_name_POST(self):
        course, response = self.create_draft_course()

        self.assertEqual(course.name, self.data_regular['name'].capitalize())

    def test_oneoff_course_create_capitalizes_name_POST(self):
        course, response = self.create_draft_oneoff_course()

        self.assertEqual(course.name, self.data_oneoff['name'].capitalize())

    # resize image
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

    # send email notification
    def test_course_create_sends_correct_email_about_pending_approval_POST(self):
        course, response = self.create_draft_course()

        course_url_admin = course.get_absolute_url_admin()
        self.assertIn(course_url_admin, mail.outbox[-1].body)

    def test_oneoff_course_create_sends_correct_email_about_pending_approval_POST(self):
        course, response = self.create_draft_oneoff_course()

        course_url_admin = course.get_absolute_url_admin()
        self.assertIn(course_url_admin, mail.outbox[-1].body)

    # redirects to detail
    def test_course_create_redirects_to_detail_POST(self):
        course, response = self.create_draft_course()

        self.assertEqual(response.url, course.get_absolute_url())

    def test_oneoff_course_create_redirects_to_detail_POST(self):
        course, response = self.create_draft_oneoff_course()

        self.assertEqual(response.url, course.get_absolute_url())

    # END OF CREATE VIEWS
    # START OF UPDATE VIEWS
    # change to draft if modified
    def test_course_update_updating_name_changes_status_to_draft_POST(self):
        course, response = self.create_published_course()

        url = reverse('course_update', args=(course.slug,))  # switches to DRAFT?
        new_name = 'Modifikovaný název'
        modified_data = model_to_dict(course)
        modified_data['name'] = new_name
        self.client.post(url, modified_data)
        course_modified = Course.objects.first()

        self.assertEqual(course.id, course_modified.id)
        self.assertEqual(course_modified.status, Course.Status.DRAFT.value)
        self.assertEqual(course_modified.name, new_name)

    def test_oneoff_course_update_updating_name_changes_status_to_draft_POST(self):
        course, response = self.create_published_oneoff_course()

        url = reverse('oneoff_course_update', args=(course.slug,))  # switches to DRAFT?
        new_name = 'Modifikovaný název jednodenní aktivity'
        modified_data = model_to_dict(course)
        modified_data['name'] = new_name
        # this is done in GET:
        modified_data['time_from'] = localtime(course.date_from).strftime('%H:%M')
        modified_data['time_to'] = localtime(course.date_to).strftime('%H:%M')

        self.client.post(url, modified_data)
        course_modified = Course.objects.first()

        self.assertEqual(course.id, course_modified.id)
        self.assertEqual(course_modified.status, Course.Status.DRAFT.value)
        self.assertEqual(course_modified.name, new_name)

    def test_course_update_updating_description_changes_status_to_draft_POST(self):
        course, response = self.create_published_course()

        url = reverse('course_update', args=(course.slug,))  # switches to DRAFT?
        new_description = 'Modifikovaný popisek aktivity.'
        modified_data = model_to_dict(course)
        modified_data['description'] = new_description
        self.client.post(url, modified_data)
        course_modified = Course.objects.first()

        self.assertEqual(course.id, course_modified.id)
        self.assertEqual(course_modified.status, Course.Status.DRAFT.value)
        self.assertEqual(course_modified.description, new_description)

    def test_oneoff_course_update_updating_description_changes_status_to_draft_POST(self):
        course, response = self.create_published_oneoff_course()

        url = reverse('oneoff_course_update', args=(course.slug,))  # switches to DRAFT?
        new_description = 'Modifikovaný popisek jednodenní aktivity.'
        modified_data = model_to_dict(course)
        modified_data['description'] = new_description
        # this is done in GET:
        modified_data['time_from'] = localtime(course.date_from).strftime('%H:%M')
        modified_data['time_to'] = localtime(course.date_to).strftime('%H:%M')

        self.client.post(url, modified_data)
        course_modified = Course.objects.first()

        self.assertEqual(course.id, course_modified.id)
        self.assertEqual(course_modified.status, Course.Status.DRAFT.value)
        self.assertEqual(course_modified.description, new_description)

    # send email notification if modified
    def test_course_update_updating_description_sends_correct_email_about_pending_reapproval_POST(self):
        course, response = self.create_published_course()
        url = reverse('course_update', args=(course.slug,))  # switches to DRAFT?

        new_description = 'Modifikovaný popisek aktivity.'
        modified_data = model_to_dict(course)
        modified_data['description'] = new_description
        self.client.post(url, modified_data)
        course_modified = Course.objects.first()
        course_url_admin = course_modified.get_absolute_url_admin()

        self.assertIn(course_url_admin, mail.outbox[-1].body)

    def test_oneoff_course_update_updating_description_sends_correct_email_about_pending_reapproval_POST(self):
        course, response = self.create_published_oneoff_course()
        url = reverse('oneoff_course_update', args=(course.slug,))  # switches to DRAFT?

        new_description = 'Modifikovaný popisek jednodenní aktivity.'
        modified_data = model_to_dict(course)
        modified_data['description'] = new_description
        # this is done in GET:
        modified_data['time_from'] = localtime(course.date_from).strftime('%H:%M')
        modified_data['time_to'] = localtime(course.date_to).strftime('%H:%M')

        self.client.post(url, modified_data)
        course_modified = Course.objects.first()
        course_url_admin = course_modified.get_absolute_url_admin()

        self.assertIn(course_url_admin, mail.outbox[-1].body)

    def test_course_update_updating_price_field_does_not_change_status_POST(self):
        course, response = self.create_published_course()

        url = reverse('course_update', args=(course.slug,))  # switches to DRAFT?
        new_price = 500
        modified_data = model_to_dict(course)
        modified_data['price'] = new_price
        self.client.post(url, modified_data)
        course_modified = Course.objects.first()

        self.assertEqual(course.id, course_modified.id)
        self.assertEqual(course_modified.status, course.status)
        self.assertEqual(course_modified.price, new_price)

    # END OF UPDATE VIEWS

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
        self.other_user = User.objects.create_user(email=OTHER_USERNAME, password=PASSWORD)
        self.client.login(email=OTHER_USERNAME, password=PASSWORD)
        url = reverse('course_detail', args=(course.slug,))  # switches to DRAFT?

        response = self.client.get(url)

        self.assertInHTML('Přístup odepřen', response.content.decode())

    def test_contact_teacher_POST(self):
        course, response = self.create_draft_course()
        data = {'sender_name': 'Stanik',
                'from_email': 'stanikuv@gmail.com',
                'body': 'Dotazující se dotazuje nějaký dotaz.'}

        self.client.post(reverse('course_contact_teacher', args=(course.slug,)), data=data)
        course_url = course.get_absolute_url()

        # [<django.core.mail.message.EmailMultiAlternatives object at 0x7fa2681b0bb0>,
        # <django.core.mail.message.EmailMessage object at 0x7fa267211fa0>]
        self.assertIn(course_url, mail.outbox[-1].body)

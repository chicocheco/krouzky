from datetime import datetime
from datetime import timedelta

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timezone import make_aware, get_default_timezone

from catalog.models import Organization, Course, AgeCategory
from invitations.models import Invitation
from users.models import User

USERNAME = 'uzivatel@seznam.cz'
INVITED_USER = 'pozvany@seznam.cz'
OTHER_INVITED_USER = 'dalsi_pozvany@seznam.cz'
PASSWORD = 'heslo123'


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

    def test_sends_notification_when_created(self):
        # using signals
        self.assertIn(f'"{self.course.name}" byla úspěšně zaregistrována a čeká na schválení', mail.outbox[-1].body)

    def test_sends_notification_when_status_changes_from_DRAFT_to_PUBLISHED(self):
        self.course.status = Course.Status.PUBLISHED
        self.course.save()

        self.assertIn(f'"{self.course.name}" byla schválena a publikována', mail.outbox[-1].body)


class InvitationModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email=USERNAME, password=PASSWORD)
        self.invitation = Invitation.objects.create(invited_email=INVITED_USER,
                                                    inviter=self.user,
                                                    date_sent=timezone.now())

    def test_str_dunder(self):
        self.assertEqual(str(self.invitation), f'Invite: {self.invitation.invited_email}')

    def test_is_key_expired_true(self):
        self.invitation.date_sent = timezone.now() - timedelta(days=3)
        self.invitation.save()

        self.assertTrue(self.invitation.is_expired())

    def test_is_expired_expired_false(self):
        self.assertFalse(self.invitation.is_expired())

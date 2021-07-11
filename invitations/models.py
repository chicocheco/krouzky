import datetime
from datetime import timedelta

from allauth.account.adapter import get_adapter
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from users.models import Coordinator


class InvitationManager(models.Manager):

    def all_expired(self):
        return self.filter(self.expired_q())

    def all_valid(self):
        return self.exclude(self.expired_q())

    def delete_expired(self):
        self.all_expired().delete()

    @staticmethod
    def expired_q():
        sent_threshold = timezone.now() - timedelta(days=3)
        q = Q(is_accepted=True) | Q(date_sent__lt=sent_threshold)  # OR
        return q


class Invitation(models.Model):
    key = models.CharField(_('klíč'), max_length=64, unique=True)
    inviter = models.ForeignKey(Coordinator, verbose_name='vytvořil', related_name='invitations',
                                on_delete=models.CASCADE)
    invited_email = models.EmailField(_('e-mailová adresa'), unique=True, max_length=40)
    is_accepted = models.BooleanField(_('přijata'), default=False)
    date_sent = models.DateTimeField(_('odeslána'), null=True)
    date_created = models.DateTimeField(_('vytvořena'), auto_now_add=True)
    objects = InvitationManager()

    @classmethod
    def create(cls, invited_email, inviter=None, **kwargs):
        key = get_random_string(64).lower()
        instance = cls._default_manager.create(invited_email=invited_email, key=key, inviter=inviter, **kwargs)
        return instance

    def is_expired(self):
        expiration_date = (self.date_sent + datetime.timedelta(days=3))
        return expiration_date <= timezone.now()

    def send_invitation(self, request, **kwargs):
        current_site = kwargs.pop('site', Site.objects.get_current())
        invite_url = reverse('accept_invite_teacher', args=(self.key,))
        invite_url = request.build_absolute_uri(invite_url)
        context = kwargs
        context.update({'invite_url': invite_url,
                        'site_name': current_site.name,
                        'invited_email': self.invited_email,
                        'inviter': self.inviter,
                        'organization': self.inviter.organization.name,
                        'key': self.key,
                        })
        email_template = 'invitations/email/email_invite'
        get_adapter().send_mail(email_template, self.invited_email, context)
        self.date_sent = timezone.now()
        self.save()

    class Meta:
        verbose_name = 'Pozvánka'
        verbose_name_plural = 'Pozvánky'

    def __str__(self):
        return f'Invite: {self.invited_email}'

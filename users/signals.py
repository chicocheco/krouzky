from allauth.account.signals import user_signed_up
from django.dispatch import receiver

from invitations.models import Invitation
from invitations.views import accept_invitation


@receiver(user_signed_up)
def accept_invite_after_signup(sender, request, user, **kwargs):
    try:
        invitation = Invitation.objects.get(invited_email=user.email)
        accept_invitation(invitation, request, user)
    except Invitation.DoesNotExist:
        pass

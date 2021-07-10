from allauth.account.adapter import get_adapter
from allauth.account.views import LoginView
from allauth.account.views import LogoutFunctionalityMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from .models import Invitation

User = get_user_model()


class AcceptExistingUserLoginView(LoginView):
    """Pre-fill the login field if an invited user has an existing account."""

    def get_initial(self):
        initial = super().get_initial()
        initial['login'] = self.request.COOKIES.pop('invited_user')
        return initial


class AcceptInviteTeacher(SingleObjectMixin, LogoutFunctionalityMixin, View):
    """
    Assign the invitee (invited user) to the inviter's organization and change their role to TEACHER.
    If the invitee does not have an account yet, their email gets pre-verified and logged in
    right after setting the password.
    """

    def get(self, request, *args, **kwargs):
        invitation = self.get_object()
        if not invitation:
            get_adapter().add_message(request, messages.ERROR, 'invitations/messages/invite_invalid.txt')
            return redirect('account_login')
        if invitation.is_accepted:
            get_adapter().add_message(request, messages.ERROR,
                                      'invitations/messages/invite_already_accepted.txt',
                                      {'invited_email': invitation.invited_email})
            return redirect('account_login')
        if invitation.is_expired():
            get_adapter().add_message(request, messages.ERROR, 'invitations/messages/invite_expired.txt',
                                      {'invited_email': invitation.invited_email})
            return redirect('account_signup')
        if request.user.is_authenticated and request.user.email != invitation.invited_email:
            self.logout()
        return render(request, 'invitations/accept_invite_teacher.html',
                      {'invited_email': invitation.invited_email,
                       'to_organization': invitation.inviter.organization})

    def post(self, request, *args, **kwargs):
        invitation = self.get_object()
        if request.user.is_authenticated and request.user.email == invitation.invited_email:
            accept_invitation(invitation, request, request.user)
            return redirect('dashboard')
        try:
            invited_user = User.objects.get(email=invitation.invited_email)
            accept_invitation(invitation, request, invited_user)
            messages.add_message(request, messages.SUCCESS, 'Přihlašte se, prosím.')
            response = redirect('invited_account_login')
            response.set_cookie('invited_user', invited_user.email)
            return response
        except User.DoesNotExist:
            pass
        # pre-verify
        get_adapter().stash_verified_email(request, invitation.invited_email)
        return redirect('account_signup')

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.get(key=self.kwargs['key'].lower())
        except Invitation.DoesNotExist:
            return None

    def get_queryset(self):
        return Invitation.objects.all()


def accept_invitation(invitation, request, invited_user):
    """Mark the invitation as used."""

    invitation.is_accepted = True
    invitation.save()
    assign_teacher_organization(invitation, invited_user)
    get_adapter().add_message(request,
                              messages.SUCCESS,
                              'invitations/messages/invite_accepted.txt',
                              {'invited_email': invitation.invited_email})


def assign_teacher_organization(invitation, invited_user):
    """Assign the organization and set TEACHER role to the invited user."""

    invited_user.organization = invitation.inviter.organization
    invited_user.role = User.Roles.TEACHER
    invited_user.save()

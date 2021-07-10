from crispy_forms.bootstrap import PrependedText
from crispy_forms.layout import Layout
from django import forms
from django.utils.translation import ugettext_lazy as _

from catalog.forms import FormHorizontalHelper
from .models import Invitation


class InviteTeacherForm(forms.Form):
    invited_email = forms.EmailField(label='E-mailová adresa zvaného')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHorizontalHelper()
        self.helper.layout = Layout(
            PrependedText('invited_email', '<i class="fas fa-envelope"></i>', placeholder='E-mailová adresa zvaného'),
        )

    def clean_invited_email(self):
        invited_email = self.cleaned_data['invited_email']
        if Invitation.objects.all_valid().filter(invited_email=invited_email, is_accepted=False):
            raise forms.ValidationError('Pozvánka byla již zaslána!')
        elif Invitation.objects.filter(invited_email=invited_email, is_accepted=True):
            raise forms.ValidationError('Pozvánka byla již použita!')
        return invited_email


# admin forms
class InvitationAdminAddForm(forms.ModelForm):
    invited_email = forms.EmailField(label=_('E-mailová adresa'), required=True)

    def save(self, *args, **kwargs):
        cd = super().clean()
        data = {'invited_email': cd.get('invited_email')}
        inviter = cd.get('inviter')
        if inviter:
            data['inviter'] = inviter
        instance = Invitation.create(**data)
        instance.send_invitation(self.request)
        super().save(*args, **kwargs)
        return instance

    def clean_invited_email(self):
        invited_email = self.cleaned_data['invited_email']
        if Invitation.objects.all_valid().filter(invited_email=invited_email, is_accepted=False):
            raise forms.ValidationError('Na tuto e-mailovou adresu již pozvánka byla zaslána.')
        elif Invitation.objects.filter(invited_email=invited_email, is_accepted=True):
            raise forms.ValidationError('Na účtu s touto e-mailovou adresou byla pozvánka již přijata.')
        return invited_email

    class Meta:
        model = Invitation
        fields = ('invited_email', 'inviter')


class InvitationAdminChangeForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ('key', 'inviter', 'invited_email', 'is_accepted', 'date_sent')

from django.contrib import admin

from .forms import InvitationAdminAddForm, InvitationAdminChangeForm
from .models import Invitation


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('invited_email', 'date_sent', 'is_accepted')

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            kwargs['form'] = InvitationAdminChangeForm
        else:
            kwargs['form'] = InvitationAdminAddForm
            kwargs['form'].request = request
        return super().get_form(request, obj, **kwargs)

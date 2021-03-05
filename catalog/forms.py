from django import forms

from .models import Organization


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ('name', 'company_id', 'vat_id', 'address', 'town', 'zip_code')

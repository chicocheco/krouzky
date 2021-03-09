from django import forms

from .models import Organization


class RegisterOrganizationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'placeholder': self.fields[field].label,
            })
            self.fields[field].label = ''

    class Meta:
        model = Organization
        fields = ('name', 'company_id', 'vat_id', 'address', 'town', 'zip_code')


class UpdateOrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ('company_id', 'vat_id', 'address', 'town', 'zip_code')


class RenameOrganizationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'placeholder': self.fields[field].label,
            })
            self.fields[field].label = ''

    class Meta:
        model = Organization
        fields = ('name',)

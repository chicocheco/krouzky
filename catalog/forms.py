from django import forms

from .models import Organization


class OrganizationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[field].label,
            })
            self.fields[field].label = ''

    class Meta:
        model = Organization
        fields = ('name', 'company_id', 'vat_id', 'address', 'town', 'zip_code')
        # labels = {'name': '', 'company_id': '', 'vat_id': '', 'address': '', 'town': '', 'zip_code': '', }
        # widgets = {
        #     'name': forms.TextInput(attrs={'placeholder': 'Název organizace', 'class': 'form-group'}),
        #     'company_id': forms.TextInput(attrs={'placeholder': 'IČO'}),
        #     'vat_id': forms.TextInput(attrs={'placeholder': 'DIČ'}),
        #     'address': forms.TextInput(attrs={'placeholder': 'Adresa'}),
        #     'town': forms.TextInput(attrs={'placeholder': 'Město'}),
        #     'zip_code': forms.TextInput(attrs={'placeholder': 'PSČ'}),
        # }

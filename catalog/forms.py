from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from .models import Organization, Course


class FormHorizontalHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-2'
        self.field_class = 'col-lg-8'
        self.form_show_labels = True
        self.add_input(Submit('submit', 'Potvrdit'))  # uses class="btn btn-primary"


class RegisterOrganizationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHorizontalHelper()

    class Meta:
        model = Organization
        fields = ('name', 'company_id', 'vat_id', 'address', 'town', 'zip_code')


class UpdateOrganizationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHorizontalHelper()

    class Meta:
        model = Organization
        fields = ('company_id', 'vat_id', 'address', 'town', 'zip_code')


class RenameOrganizationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHorizontalHelper()

    class Meta:
        model = Organization
        fields = ('name',)


class CourseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.form_show_labels = True
        self.helper.add_input(Submit('submit', 'Potvrdit'))

    class Meta:
        model = Course
        fields = ('title', 'description', 'image', 'price', 'hours', 'capacity', 'teacher', 'age_category', 'topic')

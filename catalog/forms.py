from crispy_forms.bootstrap import PrependedText, InlineCheckboxes
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Row, Column
from django import forms
from tinymce.widgets import TinyMCE

from .models import Organization, Course


class CustomTimeInput(forms.TimeInput):
    input_type = 'time'


class CustomDateInput(forms.DateTimeInput):
    input_type = 'date'

    def __init__(self, **kwargs):
        kwargs['format'] = '%Y-%m-%d'
        super().__init__(**kwargs)


class FormHorizontalHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-3'
        self.field_class = 'col-lg-9'
        self.form_show_labels = True
        self.form_show_errors = False  # displayed under navbar instead
        self.add_input(Submit('submit', 'Potvrdit'))  # uses class="btn btn-primary"


class RegisterOrganizationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHorizontalHelper()

    class Meta:
        model = Organization
        fields = ('name', 'url', 'company_id', 'vat_id', 'address', 'town', 'zip_code')


class UpdateOrganizationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHorizontalHelper()

    class Meta:
        model = Organization
        fields = ('url', 'company_id', 'vat_id', 'address', 'town', 'zip_code')


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
        self.fields['teacher'].empty_label = None  # can't create course w/o org
        self.helper = FormHelper()
        # Column() adds 'col-md' automatically
        self.helper.layout = Layout(
            'name',
            Row(
                Column('price'),
                Column('hours'),
                Column('capacity')
            ),
            Row(
                Column('date_from'),
                Column('date_to'),
            ),
            Row(
                Column('age_category'),
                Column('teacher')
            ),
            Field('image', css_class='form-control'),
            InlineCheckboxes('topic'),
            'description',
            Submit('submit', 'Potvrdit')
        )

    class Meta:
        model = Course
        fields = ('name', 'price', 'hours', 'capacity', 'date_from', 'date_to', 'teacher', 'age_category',
                  'image', 'topic', 'description')
        widgets = {
            'description': TinyMCE(),
            'topic': forms.CheckboxSelectMultiple(),
        }


class OneoffCourseForm(forms.ModelForm):
    time_from = forms.TimeField(label='Od hodin', required=True, widget=CustomTimeInput)
    time_to = forms.TimeField(label='Do hodin', required=True, widget=CustomTimeInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].empty_label = None  # can't create course w/o org
        self.fields['hours'].widget.attrs.update({'readonly': 'readonly'})
        self.fields['hours'].initial = 0
        self.fields['date_from'].label = 'Dne'
        self.helper = FormHelper()
        # Column() adds 'col-md' automatically
        self.helper.layout = Layout(
            'name',
            Row(
                Column('price'),
                Column('capacity'),
                Column('hours')
            ),
            Row(
                Column('date_from'),
                Column('time_from'),
                Column('time_to'),
            ),
            Row(
                Column('age_category'),
                Column('teacher')
            ),
            Field('image', css_class='form-control'),
            InlineCheckboxes('topic'),
            'description',
            Submit('submit', 'Potvrdit')
        )

    class Meta:
        model = Course
        fields = ('name', 'price', 'capacity', 'hours', 'date_from', 'teacher', 'age_category',
                  'image', 'topic', 'description')
        widgets = {
            'description': TinyMCE(),
            'topic': forms.CheckboxSelectMultiple(),
        }

    def save(self, commit=True):
        course = super().save(commit=False)
        clean_time_from = self.cleaned_data.get('time_from')
        clean_time_to = self.cleaned_data.get('time_to')
        if clean_time_from is not None:
            course.date_from = datetime.combine(self.cleaned_data.get('date_from'), clean_time_from)
        if clean_time_to is not None:
            course.date_to = datetime.combine(self.cleaned_data.get('date_from'), clean_time_to)
        if commit:  # maintain the default behavior
            course.save()
        return course


class ContactTeacherForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            PrependedText('sender_name', '<i class="bi bi-person-fill"></i>', placeholder='Jméno'),
            PrependedText('from_email', '<i class="bi bi-envelope-fill"></i>', placeholder='E-mailová adresa'),
            Field('body', placeholder='Co vás zajímá?', rows=5)

        )
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.form_show_errors = False

    sender_name = forms.CharField(max_length=25)
    from_email = forms.EmailField()
    body = forms.CharField(widget=forms.Textarea())


class SimpleSearchForm(forms.Form):
    query = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.disable_csrf = True
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.form_show_errors = False
        self.helper.layout = Layout(Field('query', placeholder='Zadejte klíčové slovo nebo výraz'), )


class CourseAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget = TinyMCE()

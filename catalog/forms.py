from datetime import datetime

from crispy_forms.bootstrap import PrependedText, InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Row, Column
from django import forms
from tinymce.widgets import TinyMCE

from .models import Organization, Course


class WeekScheduleInlineCheckboxes(InlineCheckboxes):
    template = 'widgets/weekschedule.html'


class CustomClearableInput(forms.ClearableFileInput):
    """
    https://stackoverflow.com/a/52184422/5258626
    """
    template_name = 'widgets/image_input.html'


class CustomTimeInput(forms.TimeInput):
    input_type = 'time'


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
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].empty_label = None  # can't create course w/o org
        self.helper = FormHelper()
        self.helper.form_id = 'course-form'
        # Column() adds 'col-md' automatically
        self.helper.layout = Layout(
            'name',
            'tags',
            'url',
            Row(
                Column('price'),
                Column('hours'),
                Column('capacity')
            ),
            Row(
                Column('date_from'),
                Column('date_to'),
            ),
            WeekScheduleInlineCheckboxes('week_schedule'),
            Row(
                Column('age_category'),
                Column('category'),
                Column('teacher')
            ),
            Field('image', css_class='form-control'),
            'x', 'y', 'width', 'height',  # hidden
            'description',
            Submit('submit_button', 'Odeslat')
            # don't use name="submit" (first arg.), it breaks .submit() function in JS
        )

    def clean(self):
        cd = self.cleaned_data
        if cd['date_from'] == cd['date_to']:
            self.add_error('date_from', 'Shoda s datem konce.')
            self.add_error('date_to', 'Shoda s datem začátku.')
        return self.cleaned_data

    class Meta:
        model = Course
        fields = (
            'name', 'tags', 'url', 'price', 'hours', 'capacity', 'date_from', 'date_to', 'week_schedule', 'teacher',
            'age_category', 'category', 'image', 'description', 'x', 'y', 'width', 'height'
        )
        widgets = {
            'description': TinyMCE(),
            'week_schedule': forms.CheckboxSelectMultiple(),
            'image': CustomClearableInput(),
        }


class OneoffCourseForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)
    time_from = forms.TimeField(label='Čas začátku', required=True, widget=CustomTimeInput)
    time_to = forms.TimeField(label='Čas konce', required=True, widget=CustomTimeInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].empty_label = None  # can't create course w/o org
        self.fields['hours'].widget.attrs.update({'readonly': 'readonly',
                                                  'style': 'pointer-events: none;',
                                                  'tabindex': "-1"})
        self.fields['hours'].initial = 0
        self.fields['date_from'].label = 'Dne'
        self.helper = FormHelper()
        self.helper.form_id = 'course-form'
        # Column() adds 'col-md' automatically
        self.helper.layout = Layout(
            'name',
            'tags',
            'url',
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
                Column('category'),
                Column('teacher')
            ),
            Field('image', css_class='form-control'),
            'x', 'y', 'width', 'height',  # hidden
            'description',
            Submit('submit_button', 'Potvrdit')
        )

    def clean(self):
        cd = self.cleaned_data
        time_from = datetime.combine(cd.get('date_from'), cd.get('time_from'))
        time_to = datetime.combine(cd.get('date_from'), cd.get('time_to'))
        if time_from > time_to:
            self.add_error('time_from', 'Čas začátku je později než čas konce.')
            self.add_error('time_to', 'Čas začátku je později než čas konce.')
        elif cd['time_from'] == cd['time_to']:
            self.add_error('time_from', 'Shoda času začátku a konce.')
            self.add_error('time_to', 'Shoda času začátku a konce.')
        return self.cleaned_data

    class Meta:
        model = Course
        fields = (
            'name', 'tags', 'url', 'price', 'capacity', 'hours', 'date_from', 'teacher', 'age_category', 'category',
            'image', 'description', 'x', 'y', 'width', 'height'
        )
        widgets = {
            'description': TinyMCE(),
            'image': CustomClearableInput(),
        }


class ContactTeacherForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            PrependedText('sender_name', '<i class="fas fa-user"></i>', placeholder='Jméno'),
            PrependedText('from_email', '<i class="fas fa-envelope"></i>', placeholder='E-mailová adresa'),
            Field('body', placeholder='Co vás zajímá?', rows=5)

        )
        self.helper.form_tag = False
        self.helper.form_show_labels = False

    sender_name = forms.CharField(max_length=25)
    from_email = forms.EmailField()
    body = forms.CharField(widget=forms.Textarea())


class CourseAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget = TinyMCE()

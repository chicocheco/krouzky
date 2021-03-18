from allauth.account.forms import LoginForm, SignupForm, ChangePasswordForm
from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.contrib.auth import get_user_model


class FormHorizontalHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-3'
        self.field_class = 'col-lg-9'
        self.form_show_labels = True
        self.add_input(Submit('submit', 'Potvrdit'))  # uses class="btn btn-primary"


class CustomLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            PrependedText('login', '<i class="bi bi-person-fill"></i>'),
            PrependedText('password', '<i class="bi bi-key-fill"></i>')
        )
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.fields['remember'].widget.attrs.update({'class': 'form-check-input'})


class CustomSignupForm(SignupForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            PrependedText('email', '<i class="bi bi-person-fill"></i>'),
            PrependedText('password1', '<i class="bi bi-key-fill"></i>'),
            PrependedText('password2', '<i class="bi bi-key-fill"></i>')
        )
        self.helper.form_tag = False
        self.helper.form_show_labels = False


class CustomChangePasswordForm(ChangePasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            PrependedText('oldpassword', '<i class="bi bi-key"></i>'),
            PrependedText('password1', '<i class="bi bi-key-fill"></i>'),
            PrependedText('password2', '<i class="bi bi-key-fill"></i>')
        )
        self.helper.form_tag = False
        self.helper.form_show_labels = False


class UserUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHorizontalHelper()
        self.fields['photo'].widget.attrs.update({
            'class': 'form-control'
        })

    class Meta:
        model = get_user_model()
        fields = ('email', 'name', 'phone', 'photo')



from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import PrependedText
from allauth.account.forms import LoginForm, SignupForm


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

        self.fields['email'].label = ''
        self.fields['password1'].label = ''
        self.fields['password2'].label = ''

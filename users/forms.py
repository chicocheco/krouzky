from allauth.account.forms import LoginForm, SignupForm
from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


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

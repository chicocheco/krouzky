from allauth.account.forms import LoginForm, SignupForm


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['login'].label = ''
        self.fields['password'].label = ''
        self.fields['remember'].widget.attrs.update({'class': 'form-check-input'})


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].label = ''
        self.fields['password1'].label = ''
        self.fields['password2'].label = ''

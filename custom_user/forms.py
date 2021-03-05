from allauth.account.forms import LoginForm


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['login'].label = ''
        self.fields['password'].label = ''
        self.fields['remember'].widget.attrs.update({'class': 'form-check-input'})

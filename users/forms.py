from PIL import Image
from allauth.account.forms import LoginForm, SignupForm, ChangePasswordForm, ResetPasswordForm, ResetPasswordKeyForm
from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Div
from django import forms
from django.contrib.auth import get_user_model


class FormHorizontalHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-3'
        self.field_class = 'col-lg-9'
        self.form_show_labels = True
        self.form_show_errors = False  # displayed under navbar instead
        self.add_input(Submit('submit', 'Potvrdit'))  # uses class="btn btn-primary"


class CustomLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            PrependedText('login', '<i class="fas fa-user"></i>'),
            PrependedText('password', '<i class="fas fa-key"></i>')
        )
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.form_show_errors = False  # displayed under navbar instead
        self.fields['remember'].widget.attrs.update({'class': 'form-check-input'})


class CustomSignupForm(SignupForm):
    conditions = forms.BooleanField(required=True,
                                    label='Souhlasím s podmínkami užívání a zásadami ochrany osobních dat')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = 'col-lg-8'
        self.fields['email'].label, self.fields['password1'].label, self.fields['password2'].label = False, False, False
        self.helper.layout = Layout(
            PrependedText('email', '<i class="fas fa-user"></i>'),
            PrependedText('password1', '<i class="fas fa-key"></i>'),
            PrependedText('password2', '<i class="fas fa-key"></i>'),
            Div(
                HTML('<ul><li><a target="_blank" href="{% url \'conditions\' %}">Podmínky užívání</a></li>'
                     '<li><a target="_blank" href="{% url \'gdpr\' %}">Zásady ochrany osobních údajů</a></li></ul>'),
                css_class='mb-3'
            ),
            'conditions',

        )
        self.helper.form_tag = False
        self.helper.form_show_errors = False  # displayed under navbar instead


class CustomChangePasswordForm(ChangePasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            PrependedText('oldpassword', '<i class="fas fa-key"></i>'),
            PrependedText('password1', '<i class="fas fa-key"></i>'),
            PrependedText('password2', '<i class="fas fa-key"></i>')
        )
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.form_show_errors = False  # displayed under navbar instead


class CustomResetPasswordForm(ResetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            PrependedText('email', '<i class="fas fa-user"></i>'),
        )
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.form_show_errors = False  # displayed under navbar instead


class CustomResetPasswordKeyForm(ResetPasswordKeyForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            PrependedText('password1', '<i class="fas fa-key"></i>'),
            PrependedText('password2', '<i class="fas fa-key"></i>')
        )
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.form_show_errors = False  # displayed under navbar instead


class UserPhotoForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.fields['photo'].widget.attrs.update({
            'class': 'form-control'
        })

    class Meta:
        model = get_user_model()
        fields = ('photo', 'x', 'y', 'width', 'height')
        widgets = {
            'photo': forms.FileInput,
        }

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)
        if user.photo:
            photo = Image.open(user.photo)
            x = self.cleaned_data.get('x')
            y = self.cleaned_data.get('y')
            w = self.cleaned_data.get('width')
            h = self.cleaned_data.get('height')
            cropped_image = photo.crop((x, y, w + x, h + y))
            resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
            resized_image.save(user.photo.path)
        return user


class UserUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHorizontalHelper()

    class Meta:
        model = get_user_model()
        fields = ('email', 'name', 'phone')

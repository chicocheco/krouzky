from pathlib import Path
from socket import gethostname, gethostbyname

import environ as django_environ  # django-environ
from django.contrib.messages import constants as messages
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent

# environmental variables
env = django_environ.Env()  # django-environ
ENVIRONMENT = env('ENVIRONMENT', default='development')
DEBUG = env.int('DEBUG', default=0)
SECRET_KEY = env('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['vyberaktivitu.online', 'www.vyberaktivitu.online'])
ALLOWED_HOSTS.extend([gethostname(), gethostbyname(gethostname())])

if ENVIRONMENT == 'production':
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'  # allows forms widget customization

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # run collectstatic manually
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.postgres',
    'django.forms',  # allows forms widget customization

    'users.apps.UsersConfig',
    'catalog.apps.CatalogConfig',

    'crispy_forms',
    'crispy_bootstrap5',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_filters',
    'tinymce',
    'taggit'
]

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    # show debug_toolbar
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True if DEBUG else False,
    }

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

if DEBUG:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# taggit (must declare both)
TAGGIT_TAGS_FROM_STRING = 'catalog.utils.comma_splitter'
TAGGIT_STRING_FROM_TAGS = 'catalog.utils.comma_joiner'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# allauth
# https://django-allauth.readthedocs.io/en/latest/advanced.html#custom-user-models
SITE_ID = 1
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
LOGIN_REDIRECT_URL = reverse_lazy('dashboard')
LOGIN_URL = reverse_lazy('account_login')  # for login_required decorator
ACCOUNT_SIGNUP_REDIRECT_URL = reverse_lazy('dashboard')
LOGOUT_REDIRECT_URL = reverse_lazy('home')
ACCOUNT_LOGOUT_ON_GET = True

ACCOUNT_FORMS = {
    'login': 'users.forms.CustomLoginForm',
    'signup': 'users.forms.CustomSignupForm',
    'change_password': 'users.forms.CustomChangePasswordForm',
    'reset_password': 'users.forms.CustomResetPasswordForm',
    'reset_password_from_key': 'users.forms.CustomResetPasswordKeyForm',
}

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'  # django 3.2

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': 5432
    }
}
if 'DATABASE_URL' in env:  # in production
    DATABASES["default"] = env.db("DATABASE_URL")  # noqa F405
    DATABASES["default"]["ATOMIC_REQUESTS"] = True  # noqa F405
    DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)  # noqa F405

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/
LANGUAGE_CODE = 'cs'
TIME_ZONE = 'Europe/Prague'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static', ]  # for dev

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
SIDE_LENGTH_COURSE_IMG = 500

# for bootstrap5
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = 'info@vyberaktivitu.online'  # for allauth

SERVER_EMAIL = 'info@vyberaktivitu.online'  # for mail_admins and mail_managers
ADMINS = [('Standa', 'stanislav.matas@gmail.com'), ]  # if DEBUG=False, sends errors
MANAGERS = [  # for pending approvals
    ('Standa', 'stanislav.matas@gmail.com'),
    # ('Klára', 'klara.matasova@gmail.com'),
]

TINYMCE_DEFAULT_CONFIG = {
    "height": "320px",
    "width": "100%",
    "placeholder": "Zde se můžete rozepsat...",
    "plugins": "autolink lists charmap preview visualblocks "
               "fullscreen paste help spellchecker",
    "menubar": False,
    "paste_as_text": True,
    "toolbar": "undo redo | bold italic underline | alignleft "
               "aligncenter alignright alignjustify | numlist bullist checklist | "
               "removeformat | charmap | "
               "fullscreen visualblocks preview",
    "custom_undo_redo_levels": 10,
    "entity_encoding": "raw",
}

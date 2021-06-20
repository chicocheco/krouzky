from .base import *

DEBUG = True

# enable django-debug-toolbar
INSTALLED_APPS += [
    'debug_toolbar',
]
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True if DEBUG else False,
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

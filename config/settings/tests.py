from .base import *

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# django-debug-toolbar is disabled during tests
# run with manage.py test --settings=config.settings.tests

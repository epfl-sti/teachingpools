from .base import *
import os

DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

INTERNAL_IPS = ['127.0.0.1',]

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware',]

INSTALLED_APPS += [
    'debug_toolbar',
    ]

EMAIL_HOST = "localhost"
EMAIL_PORT = "1025"
EMAIL_FROM = "noreply@epfl.ch"
EMAIL_SUBJECT_PREFIX = "EPFL Teaching Pools - "
EMAIL_ADMINS_EMAIL = os.environ.get('DJANGO_EMAIL_ADMINS_EMAIL', 'not@available.yet').split(',')

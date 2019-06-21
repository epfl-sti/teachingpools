from .base import *
import os
import distutils.util

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = distutils.util.strtobool(os.environ.get('DJANGO_DEBUG')) or False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DJANGO_POSTGRES_DB_NAME', 'sti_dashboards'),
        'USER': os.environ.get('DJANGO_POSTGRES_USERNAME', 'django'),
        'PASSWORD': os.environ.get('DJANGO_POSTGRES_PASSWORD', 'changeMe!'),
        'HOST': os.environ.get('DJANGO_POSTGRES_HOSTNAME', 'localhost'),
        'PORT': '',
    }
}

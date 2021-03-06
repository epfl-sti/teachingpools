from .base import *
import os


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

EMAIL_HOST = "mail.epfl.ch"
EMAIL_PORT = "25"
EMAIL_FROM = "sti-tp-noreply@epfl.ch"
EMAIL_SUBJECT_PREFIX = "EPFL Teaching Pools - "
EMAIL_ADMINS_EMAIL = os.environ.get('DJANGO_EMAIL_ADMINS_EMAIL', 'not@available.yet').split(',')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default_formatter': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/debug.log',
            'formatter': 'default_formatter',
        },
    },
    'loggers': {
        'web': {
            'handlers': ['file', ],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },
    },
}

ENVIRONMENT_TYPE = "prod"

sentry_sdk.init(
    dsn="https://42afcb097fa8406cbc7d4af140616686@sentry.io/1880740",
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
    environment="prod",
)

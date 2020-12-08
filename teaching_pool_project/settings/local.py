from .base import *
import os

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("DJANGO_POSTGRES_DB_NAME", "teaching_pool"),
        "USER": os.environ.get("DJANGO_POSTGRES_USERNAME", "postgres"),
        "PASSWORD": os.environ.get("DJANGO_POSTGRES_PASSWORD", "password"),
        "HOST": os.environ.get("DJANGO_POSTGRES_HOSTNAME", "localhost"),
        "PORT": "",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INSTALLED_APPS += [
    "debug_toolbar",
]

EMAIL_HOST = "localhost"
EMAIL_PORT = "1025"
EMAIL_FROM = "sti-tp-noreply@epfl.ch"
EMAIL_SUBJECT_PREFIX = "EPFL Teaching Pools - TEST - "
EMAIL_ADMINS_EMAIL = os.environ.get(
    "DJANGO_EMAIL_ADMINS_EMAIL", "not@available.yet"
).split(",")


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default_formatter": {
            # exact format is not important, this is the minimum information
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default_formatter",
        },
    },
    "loggers": {
        "web": {
            "handlers": [
                "console",
            ],
            "level": os.getenv("DJANGO_LOG_LEVEL", "DEBUG"),
            "propagate": True,
        },
        "django_tequila": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}

ENVIRONMENT_TYPE = "test"

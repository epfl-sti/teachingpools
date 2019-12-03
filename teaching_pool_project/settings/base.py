"""
Django settings for teaching_pool_project project.

Generated by 'django-admin startproject' using Django 1.11.20.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import distutils.util
import os
from os.path import abspath, dirname, join

from dotenv import load_dotenv

DOTENV_PATH = join(dirname(dirname(dirname(abspath(__file__)))), '.env')
load_dotenv(dotenv_path=DOTENV_PATH, verbose=True)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', os.urandom(32))


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap4',
    'web',
    'django_tequila',
    'rest_framework',
    'django_extensions',
    'mathfilters',
]

AUTH_USER_MODEL = 'web.Person'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_tequila.middleware.TequilaMiddleware',
    'epfl.sti.middlewares.authentication.LoginRequiredMiddleware',
    'epfl.sti.middlewares.authentication.ImpersonationMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'django_tequila.django_backend.TequilaBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# django_tequila related configuration
TEQUILA_SERVICE_NAME = "STI teaching pools"
TEQUILA_CLEAN_URL = True
LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_URL = "/"
LOGIN_REDIRECT_IF_NOT_ALLOWED = "/not_allowed"
LOGIN_REDIRECT_TEXT_IF_NOT_ALLOWED = "Not allowed"

# LoginRequiredMiddleware related configuration
LOGIN_EXEMPT_URLS = (
    r'^login/$',
    r'^logout/$',
)

ROOT_URLCONF = 'teaching_pool_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'web.context_processors.app_base_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'teaching_pool_project.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Zurich'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

LDAP_SERVER = 'ldap.epfl.ch'
LDAP_BASEDN = 'o=epfl,c=ch'
LDAP_FILTER = '(uid={})'
LDAP_PHD_BASEDN = 'ou=edoc,ou=etu,o=epfl,c=ch'
LDAP_PHD_FILTER = '(uniqueIdentifier={})'

EXCEL_FILE_TO_LOAD = os.environ.get('DJANGO_EXCEL_FILE_TO_LOAD', '')
EXCEL_FILE_TO_LOAD_FOR_PREVIOUS_YEAR = os.environ.get('DJANGO_EXCEL_FILE_TO_LOAD_FOR_PREVIOUS_YEAR', '')
FIRST_NAME_LAST_NAME_MAPPING = os.environ.get('DJANGO_FIRST_NAME_LAST_NAME_MAPPING', '')
PICKLED_DATA_FROM_LDAP = os.environ.get('DJANGO_PICKLED_DATA_FROM_LDAP', '')
LIST_OF_PHD_SCIPERS = os.environ.get('DJANGO_LIST_OF_PHD_SCIPERS', '')
LIST_OF_TOPICS = os.environ.get('DJANGO_LIST_OF_TOPICS', '')
EXCEL_LOADER_CURRENT_YEAR = os.environ.get('DJANGO_EXCEL_LOADER_CURRENT_YEAR', '')
EXCEL_LIST_OF_ASSIGNMENTS = os.environ.get('DJANGO_EXCEL_LIST_OF_ASSIGNMENTS', '')

COURSE_LOADER_COURSE_PICKLE_PATH = os.environ.get('DJANGO_COURSE_LOADER_COURSE_PICKLE_PATH', '')
COURSE_LOADER_CURRENT_YEAR = os.environ.get('DJANGO_COURSE_LOADER_CURRENT_YEAR', '')
COURSE_LOADER_CURRENT_TERM = os.environ.get('DJANGO_COURSE_LOADER_CURRENT_TERM', '')
COURSE_LOADER_TEACHERS_PICKLE_PATH = os.environ.get('DJANGO_COURSE_LOADER_TEACHERS_PICKLE_PATH', '')

APP_BASE_URL = os.environ.get('DJANGO_APP_BASE_URL', 'https://localhost')

DEBUG = distutils.util.strtobool(os.environ.get('DJANGO_DEBUG')) or False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

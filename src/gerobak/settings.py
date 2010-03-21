DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'gerobak.db'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

TIME_ZONE = 'Europe/Amsterdam'

LANGUAGE_CODE = 'en'

SITE_ID = 1

USE_I18N = False

import os
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')

MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = '/admin/media/'

SECRET_KEY = '0de76fa976675faac04a778a0ee6a5bfc07a8c37bf1c890ad548a3ce'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
)

ROOT_URLCONF = 'gerobak.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'gerobak',
    'gerobak.apps.profile',
    'registration',
    'celery',
    'ghettoq',
)

FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

ACCOUNT_ACTIVATION_DAYS = 7
EMAIL_HOST='127.0.0.1'

LOGIN_REDIRECT_URL = '/'

GEROBAK_ARCHS = (
    ('i386', 'i386'),
    ('amd64', 'amd64'),
)
GEROBAK_DEFAULT_ARCH = 'i386'

GEROBAK_APT_GET = '/usr/bin/apt-get'
GEROBAK_APT_CACHE = '/usr/bin/apt-cache'
GEROBAK_WORKING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                   'work')

EMAIL_PORT = 1025

CELERY_BACKEND = 'database'
CELERY_IMPORTS = ("gerobak.apps.profile.tasks", )
CARROT_BACKEND = "ghettoq.taproot.Database"


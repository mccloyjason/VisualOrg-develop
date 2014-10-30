"""
Django settings for visualorg project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'oba!e*cr*&zb+hv9pt%&4yesjznt%lziel^h*rf--m2&j=g%ix'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'admin_shortcuts',
    'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'apps.accounts',
    'apps.alerts',
    'django_nose',
    'apps.billing',
    'apps.contact',
    'apps.documents',
    'apps.processes',
    'apps.questions',
    'apps.utils',
    'rest_framework',

)

SITE_ID=1

ADMIN_SHORTCUTS = [
    {

        'shortcuts': [
             {
                    'url': '/',
                    'open_new_window': True,
                },
            {
                'url_name': 'admin:questions_question_changelist',
                'title': 'Questions',
            },
            {
                'url_name': 'admin:processes_process_changelist',
                'title': 'Process',
            },
            {
                'url_name': 'admin:accounts_user_changelist',
                'title': 'Users',
            },
            {
                'url_name': 'admin:billing_paymentplan_changelist',
                'title': 'Billing',
            },
            {
                'url_name': 'admin:contact_contactformentry_changelist',
                'title': 'Contacts',
            },

        ]
    },

]

ADMIN_SHORTCUTS_SETTINGS = {

    'open_new_window': False,
}

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
)

ROOT_URLCONF = 'visualorg.urls'

WSGI_APPLICATION = 'visualorg.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'staticfiles'),)

STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
)

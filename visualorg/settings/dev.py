from visualorg.settings import *

SECRET_KEY = 'oba!e*cr*&zb+hv9pt%&4yesjznt%lziel^h*rf--m2&j=g%ix'
DEBUG=True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME':'visualorg_db',
        'USER':'visualorg',
        'PASSWORD':'visualorg',
        'HOST':'54.200.253.8',
        'PORT':'5432',
    }
}

EMAIL_SUBJECT_PREFIX = "[Visual Org]"

EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_HOST_PASSWORD = 'developer'
EMAIL_HOST_USER     = 'devteamrnds@gmail.com'
DEFAULT_FROM_EMAIL  ="devteamrnds@gmail.com"
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True

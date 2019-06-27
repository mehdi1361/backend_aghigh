from .base import *

DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "94.182.227.16", "aghigh.ayandehsazan.ir"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'aghigh_backend',
        'USER': 'agu6756v',
        'PASSWORD': 'dfsdfdf#$$^^#QsAD$KxsBgVdzPAU=565kzWG3mVsW',
        'HOST': 'localhost',
        'PORT': '',
        'CONN_MAX_AGE': 60,
    },
    '96_97': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'aghigh_backend_96_97',
        'USER': 'agu6756v',
        'PASSWORD': 'dfsdfdf#$$^^#QsAD$KxsBgVdzPAU=565kzWG3mVsW',
        'HOST': 'localhost',
        'PORT': '',
    }
}

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

RAVEN_CONFIG = {
    'dsn': 'http://a6287c78ee704adfa117a62da6d8628b:783babfbcee54bf78c18c52ec51b6183@37.59.208.96:9000/38',
}

RABBIT_MQ_USER = 'guest'
RABBIT_MQ_PASS = '!@#1231370'

MONGO = {
    'HOST': '188.253.3.155',
    'PORT': 59833,
}

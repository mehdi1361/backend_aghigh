from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'aghigh_backend',
        'USER': 'postgres',
        'PASSWORD': '13610522',
        'HOST': 'localhost',
        'PORT': '',
        'CONN_MAX_AGE': 60,
        # 'OPTIONS': {
        #     'MAX_CONNS': 100
        # }
    },
    # '96_97': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'aghigh_backend_96_97',
    #     'USER': 'agu6756v',
    #     'PASSWORD': 'dfsdfdf#$$^^#QsAD$KxsBgVdzPAU=565kzWG3mVsW',
    #     'HOST': 'localhost',
    #     'PORT': '',
    # }
}

MONGO = {
    'HOST': '127.0.0.1',
    'PORT': 27017,
}

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

RABBIT_MQ_USER = 'guest'
RABBIT_MQ_PASS = '!@#1231370'

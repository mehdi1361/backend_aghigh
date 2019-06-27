import os
import datetime
import logging.config
from django.conf import settings
import logging

LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format':
                '[START]-[AT]:%(asctime)s \n' +
                '[LEVEL]:%(levelname)s\n' +
                '[FILE]:%(pathname)s\n' +
                '[LINE]:%(lineno)d\n' +
                '[PROCESS]:%(process)d ' +
                '[THREAD]:%(thread)d\n' +
                '[DETAIL]:%(detail)s\n'
                '[MESSAGE]:%(message)s\n'
                '[END]\n-----------------------------\n'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': settings.LOGS_ROOT + '/{}.log'.format(datetime.datetime.now().strftime('%Y_%m_%d')),
            'formatter': 'verbose'
        },
        # 'console': {
        #     'class': 'logging.StreamHandler',
        # },
    },
    'loggers': {
        'dashboard': {
            'handlers': ['file'],
            # 'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

LOGGING_BAGHERY = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'sentry': {
            'class': 'dashboard.sentry.CustomHandlerSentry',
            'dsn': 'http://753a94dde90d41cf8632e8b408d9f6e8:600d80be94dc49a0baa581629d07288d@37.59.208.96:9000/36'
        },
    },
    'loggers': {
        'bagheri_api': {
            'handlers': ['sentry'],
            'level': 'DEBUG',  # change debug level as appropiate
            'propagate': True,
        }
    },
}

# LOGGING_WEB = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'sentry': {
#             'class': 'dashboard.sentry.CustomHandlerSentry',
#             'dsn': 'http://2a68552287bf486a8c7a6e963233bbeb:164abf1e238c447894a3b71cc13f6d53@37.59.208.96:9000/39',
#         },
#     },
#     'loggers': {
#         'bagheri_api': {
#             'handlers': ['sentry'],
#             'level': 'DEBUG',  # change debug level as appropiate
#             'propagate': True,
#         }
#     },
# }

if not os.path.exists(settings.LOGS_ROOT):

    """
        check if log path does not exit
    """

    try:
        os.mkdir(settings.LOGS_ROOT)

    except OSError as e:
        exit(0)

logging.config.dictConfig(LOGGING)
logger_v1 = logging.getLogger("dashboard")

logging.config.dictConfig(LOGGING_BAGHERY)
logger_api = logging.getLogger("bagheri_api")

# logging.config.dictConfig(LOGGING_WEB)
# logger_web = logging.getLogger("aghigh_web")
from eshot_api.settings import *
from selenium import webdriver
import json

# Middlewares
INDEPENDENT_MIDDLEWARES = []
DEPENDENT_MIDDLEWARES = []

MIDDLEWARE_CLASSES += INDEPENDENT_MIDDLEWARES + DEPENDENT_MIDDLEWARES

# Apps
INDEPENDENT_APPS = [
    "rest_framework",
    "django_extensions"
]

DEPENDENT_APPS = [
    "izmir"
]

INSTALLED_APPS += INDEPENDENT_APPS + DEPENDENT_APPS

# Static
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

STATIC_ROOT = "/var/www/eshot_api/static"
MEDIA_ROOT = "/var/www/eshot_api/media"

# Database
with open("config.json", "r") as f:
    DATABASES = json.loads(f.read())["database"]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'streamer': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'mirror': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/eshot_api/mirror.log',
        },
        'tracker': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/eshot_api/tracker.log'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['streamer', 'tracker'],
            'level': 'INFO',
            'propagate': True,
        },
        'scripts.update_stops': {
            'handlers': ['streamer', 'mirror', 'tracker'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'scripts.update_routes': {
            'handlers': ['streamer', 'mirror', 'tracker'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'scripts.update_routes_2': {
            'handlers': ['streamer', 'mirror', 'tracker'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}

# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning'
}

################
# Special Conf #
################
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
    "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
]

POLITE_REQ_LIMIT = 90
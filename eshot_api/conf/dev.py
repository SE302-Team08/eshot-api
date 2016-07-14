from eshot_api.settings import *
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
        }
    },
}

# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning'
}
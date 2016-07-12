from eshot_api.settings import *
import json

# Middlewares
INDEPENDENT_MIDDLEWARES = []
DEPENDENT_MIDDLEWARES = []

MIDDLEWARE_CLASSES += INDEPENDENT_MIDDLEWARES + DEPENDENT_MIDDLEWARES

# Apps
INDEPENDENT_APPS = [
    "rest_framework"
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


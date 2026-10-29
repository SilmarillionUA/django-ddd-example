# Copy to local.py and fill in. local.py is ignored by git.
from .develop import *

SECRET_KEY = ""

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "library",
        "USER": "",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "5432",
    },
}

INTERNAL_IPS = ("127.0.0.1",)

MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)
INSTALLED_APPS += ("debug_toolbar",)

if not SECRET_KEY or not DATABASES["default"]["PASSWORD"]:
    raise NotImplementedError("Set SECRET_KEY and DATABASES in local.py")

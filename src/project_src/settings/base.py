import os
import sys

from celery.schedules import crontab

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = False

PROJECT_ROOT = os.path.abspath(BASE_DIR)  # project_src/
MANAGE_ROOT = os.path.dirname(PROJECT_ROOT)  # src/
REPOSITORY_ROOT = os.path.dirname(MANAGE_ROOT)  # repository root


def join_to_repo(slug: str) -> str:
    return os.path.join(REPOSITORY_ROOT, slug)


def join_to_project(slug: str) -> str:
    return os.path.join(PROJECT_ROOT, slug)


def join_to_manage(slug: str) -> str:
    return os.path.join(MANAGE_ROOT, slug)


# Apps import each other as `catalog`, not `apps.catalog`.
sys.path.insert(0, join_to_manage("apps"))

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")

ALLOWED_HOSTS: list[str] = []

LOCAL_APPS = (
    "catalog",
    "lending",
)

INSTALLED_APPS = (
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "rest_framework",
    *LOCAL_APPS,
)

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

ROOT_URLCONF = "project_src.urls"
WSGI_APPLICATION = "project_src.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Each app keeps its templates in infrastructure/templates, which
        # the app loader never looks at, so every app is listed here.
        # APP_DIRS stays on for the admin and Unfold templates.
        "DIRS": [
            join_to_project("templates"),
            join_to_manage("apps/catalog/infrastructure/templates"),
            join_to_manage("apps/lending/infrastructure/templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Migrations live in infrastructure/, where Django does not look.
MIGRATION_MODULES = {
    "catalog": "catalog.infrastructure.migrations",
    "lending": "lending.infrastructure.migrations",
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = join_to_manage("allstatic")
MEDIA_URL = "/media/"
MEDIA_ROOT = join_to_manage("media")

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "lending:my_loans"
LOGOUT_REDIRECT_URL = "catalog:book_list"

DEFAULT_FROM_EMAIL = "library@example.com"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    "lending-send-due-reminders": {
        "task": "lending.infrastructure.tasks.send_due_reminders",
        "schedule": crontab(hour=8, minute=0),
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        app: {"handlers": ["console"], "level": "INFO", "propagate": False}
        for app in LOCAL_APPS
    },
}

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_src.settings.local")

app = Celery("project_src")
app.conf.worker_hijack_root_logger = False
app.config_from_object("django.conf:settings", namespace="CELERY")

# Tasks live in infrastructure/tasks.py, so the default lookup of
# <app>.tasks would find nothing.
app.autodiscover_tasks(
    lambda: [
        "catalog.infrastructure",
        "lending.infrastructure",
    ]
)

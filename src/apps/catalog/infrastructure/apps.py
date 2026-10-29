from importlib import import_module

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CatalogConfig(AppConfig):
    name = "catalog"
    label = "catalog"
    verbose_name = _("Catalog")

    def import_models(self) -> None:
        # Models live in domain/models.py, not <app>/models.py. Setting
        # models_module keeps post_migrate signals (permissions, content
        # types) firing for this app.
        self.models = self.apps.all_models[self.label]
        self.models_module = import_module("catalog.domain.models")

    def ready(self) -> None:
        # Admin autodiscovery imports <app>.admin, which does not exist.
        import_module("catalog.infrastructure.admin")

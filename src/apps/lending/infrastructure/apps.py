from importlib import import_module

from django.apps import AppConfig
from django.core.management import get_commands
from django.utils.translation import gettext_lazy as _

# Commands live in infrastructure/management/, which Django's command
# finder does not scan, so each one is registered by name.
MANAGEMENT_COMMANDS = ("send_due_reminders",)
COMMANDS_PACKAGE = "lending.infrastructure"


class LendingConfig(AppConfig):
    name = "lending"
    label = "lending"
    verbose_name = _("Lending")

    def import_models(self) -> None:
        # Models live in domain/models.py, not <app>/models.py. Setting
        # models_module keeps post_migrate signals (permissions, content
        # types) firing for this app.
        self.models = self.apps.all_models[self.label]
        self.models_module = import_module("lending.domain.models")

    def ready(self) -> None:
        # Admin autodiscovery imports <app>.admin, which does not exist.
        import_module("lending.infrastructure.admin")

        commands = get_commands()
        for command_name in MANAGEMENT_COMMANDS:
            commands[command_name] = COMMANDS_PACKAGE

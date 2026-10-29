from django.db import models
from django.utils.translation import gettext_lazy as _


class CopyCondition(models.TextChoices):
    GOOD = "good", _("Good")
    WORN = "worn", _("Worn")
    DAMAGED = "damaged", _("Damaged")

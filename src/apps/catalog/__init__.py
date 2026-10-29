import sys

from catalog.infrastructure import apps

# Django looks for <app>.apps. The config lives in infrastructure/.
sys.modules["catalog.apps"] = apps

import sys

from lending.infrastructure import apps

# Django looks for <app>.apps. The config lives in infrastructure/.
sys.modules["lending.apps"] = apps

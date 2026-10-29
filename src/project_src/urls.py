from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("catalog.infrastructure.urls")),
    path("loans/", include("lending.infrastructure.urls")),
    path("api/lending/", include("lending.infrastructure.api_urls")),
]

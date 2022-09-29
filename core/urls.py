# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("secret/", admin.site.urls),  # Django admin route
    path("admin/", include('admin_honeypot.urls', namespace='admin_honeypot')),
    path("", include("apps.authentication.urls")),  # Auth routes - login / register
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Leave `Home.Urls` as last the last line ALWAYS!
urlpatterns += [path("", include("apps.home.urls"))]

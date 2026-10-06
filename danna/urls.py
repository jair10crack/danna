from django.contrib import admin
from django.apps import apps
from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gestion.urls')),
]

if settings.DEBUG and apps.is_installed('django_browser_reload'):
    urlpatterns.append(path('__reload__/', include('django_browser_reload.urls')))

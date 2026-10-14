from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from core.views_system import health, routes_manifest

urlpatterns = [
    path('health/', health, name='health'),
    path('manus-routes.json', routes_manifest, name='routes_manifest'),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

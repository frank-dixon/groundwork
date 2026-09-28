from django.contrib import admin
from django.urls import include, path

from garden import views as garden_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sw.js', garden_views.service_worker, name='service_worker'),
    path('manifest.webmanifest', garden_views.manifest, name='manifest'),
    path('', include('garden.urls')),
]

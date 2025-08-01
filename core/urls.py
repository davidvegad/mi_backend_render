from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views  # <-- 1. Importa el archivo de vistas del core


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', views.health_check, name='health_check'),
    path('api/', include('api.urls')), # Incluimos las URLs de nuestra app
    path('psychology/api/', include('psychology_api.urls')),
    path('api/servicios/', include('servicios_web.urls')),
    path('api/linkinbio/', include('links.urls')), # Temporalmente comentado por error de dependencia
    path('api/timehub/', include('timehub.urls')),
    path('api/kanban/', include('task_manager.urls')),
    path('api/pacifik/', include('pacifik.urls')),
    
]

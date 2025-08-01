from django.urls import path
from . import views

app_name = 'pacifik'

urlpatterns = [
    # Autenticación
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Áreas comunes
    path('areas/', views.AreaListCreateView.as_view(), name='area-list-create'),
    path('areas/<int:pk>/', views.AreaDetailView.as_view(), name='area-detail'),
    
    # Reservas
    path('reservas/', views.ReservaListCreateView.as_view(), name='reserva-list-create'),
    path('reservas/<int:pk>/', views.ReservaDetailView.as_view(), name='reserva-detail'),
    
    # Disponibilidad
    path('disponibilidad/', views.consultar_disponibilidad, name='consultar-disponibilidad'),
    
    # Estadísticas
    path('estadisticas/', views.estadisticas_usuario, name='estadisticas-usuario'),
    
    # Reservas públicas
    path('reservas/todas/', views.todas_las_reservas, name='todas-las-reservas'),
    
    # Admin endpoints
    path('admin/reservas/', views.AdminReservaListView.as_view(), name='admin-reservas'),
    
    # Cron webhook
    path('cron/complete-reservations/', views.auto_complete_reservations_webhook, name='cron-complete-reservations'),
]
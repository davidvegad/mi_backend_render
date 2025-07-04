# psychology_api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Se usan "basenames" para evitar colisiones con otras apps
router.register(r'profile', views.ProfileViewSet, basename='psychology-profile')
router.register(r'services', views.ServiceViewSet, basename='psychology-service')
router.register(r'testimonials', views.TestimonialViewSet, basename='psychology-testimonial')
router.register(r'posts', views.PostViewSet, basename='psychology-post')
router.register(r'contact', views.ContactSubmissionViewSet, basename='psychology-contact')
router.register(r'books', views.BookViewSet, basename='psychology-book') # Nuevo endpoint para libros

urlpatterns = [
    path('', include(router.urls)),
    path('settings/', views.SiteSettingsView.as_view(), name='site-settings'),
    # Nuevas rutas para el proceso de pago
    path('create-payment-preference/', views.CreatePaymentPreferenceView.as_view(), name='create-payment-preference'),
    path('mercadopago-webhook/', views.MercadoPagoWebhookView.as_view(), name='mercadopago-webhook'),
]

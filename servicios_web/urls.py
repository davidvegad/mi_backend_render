from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServicioViewSet, PaqueteViewSet, ArticuloBlogViewSet, PreguntaFrecuenteViewSet, ContactoAPIView

router = DefaultRouter()
router.register(r'servicios', ServicioViewSet)
router.register(r'paquetes', PaqueteViewSet)
router.register(r'blog', ArticuloBlogViewSet)
router.register(r'preguntas-frecuentes', PreguntaFrecuenteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('contacto/', ContactoAPIView.as_view(), name='contacto'),
]
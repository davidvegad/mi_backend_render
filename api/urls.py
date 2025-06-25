# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoticiaViewSet, JugadorViewSet, HeroSlideViewSet, PartidoViewSet, SponsorViewSet

# Crea un router y registra nuestro viewset con él.
router = DefaultRouter()
router.register(r'jugadores', JugadorViewSet)
router.register(r'noticias', NoticiaViewSet)
router.register(r'heroslides', HeroSlideViewSet)
router.register(r'partidos', PartidoViewSet)
router.register(r'sponsors', SponsorViewSet)

# Las URLs de la API son determinadas automáticamente por el router.
urlpatterns = [
    path('', include(router.urls)),
]
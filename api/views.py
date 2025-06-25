from django.shortcuts import render
# api/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Jugador, Noticia, Sponsor, Partido, HeroSlide
from .serializers import JugadorSerializer, SponsorSerializer, PartidoSerializer, HeroSlideSerializer, NoticiaSerializer

class NoticiaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Este ViewSet provee automáticamente las acciones `list` (listar todos)
    y `retrieve` (obtener uno por id).
    """
    queryset = Noticia.objects.all().order_by('fecha')
    serializer_class = NoticiaSerializer
    
    def get_serializer_context(self):
        # Añade el request al contexto
        return {'request': self.request}

class JugadorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Este ViewSet provee automáticamente las acciones `list` (listar todos)
    y `retrieve` (obtener uno por id).
    """
    queryset = Jugador.objects.all().order_by('nombre')
    serializer_class = JugadorSerializer
    
    def get_serializer_context(self):
        # Añade el request al contexto
        return {'request': self.request}
    
class HeroSlideViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Este ViewSet provee automáticamente las acciones `list` (listar todos)
    y `retrieve` (obtener uno por id).
    """
    queryset = HeroSlide.objects.all().order_by('orden')
    serializer_class = HeroSlideSerializer
    
    def get_serializer_context(self):
        # Añade el request al contexto
        return {'request': self.request}
    
class PartidoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Este ViewSet provee automáticamente las acciones `list` (listar todos)
    y `retrieve` (obtener uno por id).
    """
    queryset = Partido.objects.all().order_by('fecha')
    serializer_class = PartidoSerializer
    
    def get_serializer_context(self):
        # Añade el request al contexto
        return {'request': self.request}
        
    @action(detail=False, methods=['get'])
    def proximos(self, request):
        """Endpoint para obtener solo los próximos partidos."""
        proximos_partidos = Partido.objects.filter(fecha__gte=timezone.now()).order_by('fecha')
        serializer = self.get_serializer(proximos_partidos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def resultados(self, request):
        """Endpoint para obtener solo los partidos ya jugados."""
        resultados_partidos = Partido.objects.filter(fecha__lt=timezone.now()).order_by('-fecha')
        serializer = self.get_serializer(resultados_partidos, many=True)
        return Response(serializer.data)
    
class SponsorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Este ViewSet provee automáticamente las acciones `list` (listar todos)
    y `retrieve` (obtener uno por id).
    """
    queryset = Sponsor.objects.all().order_by('nombre')
    serializer_class = SponsorSerializer    
    
    def get_serializer_context(self):
        # Añade el request al contexto
        return {'request': self.request}
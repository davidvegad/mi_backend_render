# api/serializers.py
from rest_framework import serializers
from .models import Jugador, Noticia, HeroSlide, Sponsor, Partido

class NoticiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Noticia
        fields = '__all__' # Incluye todos los campos

class JugadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jugador
        fields = '__all__' # Incluye todos los campos
        
class HeroSlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSlide
        fields = '__all__' # Incluye todos los campos        

class PartidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partido
        fields = '__all__' # Incluye todos los campos
        
class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsor
        fields = '__all__' # Incluye todos los campos        
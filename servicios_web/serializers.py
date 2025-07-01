from rest_framework import serializers
from .models import Servicio, Paquete, ArticuloBlog, PreguntaFrecuente

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'

class PaqueteSerializer(serializers.ModelSerializer):
    precio = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    class Meta:
        model = Paquete
        fields = '__all__'

class ArticuloBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticuloBlog
        fields = '__all__'

class PreguntaFrecuenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreguntaFrecuente
        fields = '__all__'

class ContactoSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    asunto = serializers.CharField(max_length=200)
    mensaje = serializers.CharField()

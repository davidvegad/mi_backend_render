from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import send_mail

from .models import Servicio, Paquete, ArticuloBlog, PreguntaFrecuente
from .serializers import ServicioSerializer, PaqueteSerializer, ArticuloBlogSerializer, PreguntaFrecuenteSerializer, ContactoSerializer

class ServicioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer

class PaqueteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Paquete.objects.all()
    serializer_class = PaqueteSerializer

class ArticuloBlogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArticuloBlog.objects.all()
    serializer_class = ArticuloBlogSerializer
    lookup_field = 'slug'

class PreguntaFrecuenteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PreguntaFrecuente.objects.all()
    serializer_class = PreguntaFrecuenteSerializer

class ContactoAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ContactoSerializer(data=request.data)
        if serializer.is_valid():
            nombre = serializer.validated_data.get('nombre')
            email = serializer.validated_data.get('email')
            asunto = serializer.validated_data.get('asunto')
            mensaje = serializer.validated_data.get('mensaje')

            # Construir el mensaje de correo
            email_subject = f"Mensaje de contacto de {nombre}: {asunto}"
            email_body = f"De: {nombre} <{email}>\n\nMensaje:\n{mensaje}"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [settings.CONTACT_FORM_RECIPIENT]

            try:
                send_mail(email_subject, email_body, from_email, recipient_list, fail_silently=False)
                return Response({"message": "Mensaje enviado con éxito"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": f"Error al enviar el mensaje: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# psychology_api/views.py

from rest_framework.views import APIView # <-- Importar APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Profile, Service, Testimonial, Post, ContactSubmission, SiteSettings 
from .serializers import (
    ProfileSerializer, ServiceSerializer, TestimonialSerializer, 
    PostSerializer, ContactSubmissionSerializer, SiteSettingsSerializer 
)
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.filter(user__is_active=True)
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

class TestimonialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Testimonial.objects.filter(is_visible=True)
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]

class PostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.filter(status='published')
    serializer_class = PostSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

class ContactSubmissionViewSet(viewsets.ModelViewSet):
    # ... (queryset, serializer_class, etc. se quedan igual) ...
    queryset = ContactSubmission.objects.all()
    serializer_class = ContactSubmissionSerializer
    http_method_names = ['post']

    def perform_create(self, serializer):
        instance = serializer.save()
        
        # --- Notificación por Email ---
        try:
            # 1. Email para la psicóloga (el que ya teníamos)
            subject_to_psychologist = f"Nuevo Mensaje de Contacto: {instance.name}"
            message_to_psychologist = f"""
            Has recibido un nuevo mensaje desde tu página web:

            Nombre: {instance.name}
            Email: {instance.email}
            Mensaje:
            {instance.message}

            Puedes responder directamente a {instance.email}.
            """
            send_mail(
                subject_to_psychologist,
                message_to_psychologist,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_FORM_RECIPIENT],
                fail_silently=False,
            )

            # 2. (MEJORA) Email de confirmación para el usuario
            subject_to_user = "Hemos recibido tu mensaje"
            message_to_user = f"""
            Hola {instance.name},

            Gracias por ponerte en contacto. Hemos recibido tu mensaje y te responderemos lo antes posible.

            Este es un resumen de tu consulta:
            "{instance.message}"

            Saludos,
            Psicóloga [Nombre]
            """
            send_mail(
                subject_to_user,
                message_to_user,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email], # Se envía al email que el usuario proporcionó
                fail_silently=False,
            )

        except Exception as e:
            logger.error(f"Error al enviar email de contacto: {e}")
            
class SiteSettingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Obtenemos la primera (y única) instancia de configuración
        settings = SiteSettings.objects.first()
        if settings:
            serializer = SiteSettingsSerializer(settings)
            return Response(serializer.data)
        # Si no se ha creado ninguna configuración, devuelve un objeto vacío
        return Response({})            
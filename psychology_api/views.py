# psychology_api/views.py

from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Profile, Service, Testimonial, Post, ContactSubmission, SiteSettings, Book
from .serializers import (
    ProfileSerializer, ServiceSerializer, TestimonialSerializer, 
    PostSerializer, ContactSubmissionSerializer, SiteSettingsSerializer, BookSerializer
)
from django.core.mail import send_mail
from django.conf import settings
import logging
import mercadopago
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# --- VISTAS EXISTENTES ---

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
    queryset = ContactSubmission.objects.all()
    serializer_class = ContactSubmissionSerializer
    http_method_names = ['post']

    def perform_create(self, serializer):
        instance = serializer.save()
        
        try:
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
                [instance.email],
                fail_silently=False,
            )

        except Exception as e:
            logger.error(f"Error al enviar email de contacto: {e}")
            
class SiteSettingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        settings_obj = SiteSettings.objects.first()
        if settings_obj:
            serializer = SiteSettingsSerializer(settings_obj)
            return Response(serializer.data)
        return Response({})

# --- VISTAS PARA LIBROS Y PAGOS ---

class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.filter(is_published=True)
    serializer_class = BookSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

class CreatePaymentPreferenceView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        book_slug = request.data.get('slug')
        if not book_slug:
            return Response({"error": "No se proporcionó el slug del libro."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book = Book.objects.get(slug=book_slug, is_published=True)
        except Book.DoesNotExist:
            return Response({"error": "El libro no existe o no está disponible."}, status=status.HTTP_404_NOT_FOUND)

        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

        preference_data = {
            "items": [
                {
                    "title": f"{book.title} - por {book.author}" if book.author else book.title,
                    "picture_url": book.cover_image.url, # URL de la imagen de portada
                    "description": book.description.split('\n')[0], # Primera línea de la descripción
                    "id": str(book.id), # ID del libro en tu sistema
                    "quantity": 1,
                    "unit_price": float(book.price),
                    "currency_id": "PEN", # Moneda Peruana
                }
            ],
            "back_urls": {
                "success": f"{settings.FRONTEND_URL}/compra-exitosa",
                "failure": f"{settings.FRONTEND_URL}/compra-fallida",
                "pending": f"{settings.FRONTEND_URL}/compra-pendiente"
            },
            "external_reference": str(book.id), # Referencia para nuestro webhook
        }

        if not settings.DEBUG:
            preference_data["auto_return"] = "approved"
            preference_data["notification_url"] = f"https://{settings.RENDER_HOSTNAME}/api/psychology/mercadopago-webhook/"
        
        logger.info(f"Enviando preferencia de pago a Mercado Pago: {preference_data}")

        try:
            preference_response = sdk.preference().create(preference_data)
            
            if preference_response and preference_response.get("status") in [200, 201]:
                preference = preference_response["response"]
                return Response({'preference_id': preference['id']}, status=status.HTTP_201_CREATED)
            else:
                error_message = preference_response.get("message", "Error desconocido de Mercado Pago")
                logger.error(f"Error de Mercado Pago al crear preferencia: {error_message}. Respuesta completa: {preference_response}")
                return Response({"error": f"Error de Mercado Pago: {error_message}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Excepción al crear preferencia de pago: {e}")
            return Response({"error": "No se pudo crear la preferencia de pago."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MercadoPagoWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if request.data.get("action") == "payment.created":
            payment_id = request.data.get("data", {}).get("id")
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)["response"]

            if payment_info.get("status") == "approved":
                book_id = payment_info.get("external_reference")
                payer_email = payment_info.get("payer", {}).get("email")
                
                try:
                    book = Book.objects.get(id=int(book_id))
                    download_url = create_presigned_url(settings.AWS_STORAGE_BUCKET_NAME, book.pdf_file.name)
                    
                    # Enviar email con el enlace de descarga
                    send_download_link_email(payer_email, book, download_url)

                except (Book.DoesNotExist, ClientError) as e:
                    logger.error(f"Error al procesar webhook para pago aprobado {payment_id}: {e}")

        return Response(status=status.HTTP_200)

# --- FUNCIONES AUXILIARES ---

def create_presigned_url(bucket_name, object_name, expiration=3600):
    s3_client = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logger.error(f"Error al generar URL pre-firmada: {e}")
        return None
    return response

def send_download_link_email(user_email, book, download_url):
    subject = f"Tu enlace de descarga para: {book.title}"
    message = f"""
    ¡Gracias por tu compra!

    Aquí tienes tu enlace para descargar "{book.title}".
    Este enlace es único y expirará en 1 hora.

    Enlace de descarga: {download_url}

    Si tienes algún problema, no dudes en contactarnos.

    Saludos,
    Psicóloga [Nombre]
    """
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Error al enviar email con enlace de descarga a {user_email}: {e}")
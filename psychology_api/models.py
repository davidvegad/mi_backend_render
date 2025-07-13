# psychology_api/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from storages.backends.s3boto3 import S3Boto3Storage

# Si tienes una configuración global en settings.py, no necesitas instanciar aquí.
# Pero si quieres ser explícito, puedes hacerlo así.
s3_storage = S3Boto3Storage()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='psychology_profile', help_text="Asociar con un usuario de Django para la psicóloga")
    bio = models.TextField(help_text="Biografía profesional de la psicóloga.")
    philosophy = models.TextField(help_text="Enfoque y filosofía de trabajo.")
    # Campo de imagen que se subirá a S3 a la carpeta 'profile_photos/'
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True, help_text="Foto profesional de la psicóloga.", storage=s3_storage)
    professional_id = models.CharField(max_length=50, blank=True, help_text="Número de colegiada.")

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Service(models.Model):
    title = models.CharField(max_length=200, help_text="Ej: Terapia Individual")
    slug = models.SlugField(max_length=200, unique=True, help_text="Versión amigable para URL, ej: terapia-individual")
    description = models.TextField(help_text="Descripción detallada del servicio.")
    # Imagen ilustrativa del servicio, se subirá a S3
    image = models.ImageField(upload_to='service_images/', blank=True, null=True, help_text="Imagen representativa del servicio.", storage=s3_storage)
    order = models.PositiveIntegerField(default=0, help_text="Para ordenar los servicios en la web.")
    
    # --- CAMPOS NUEVOS ---
    whatsapp_number = models.CharField(
        max_length=20, 
        blank=True, 
        help_text="Número de WhatsApp específico para este servicio (ej. 51948362849). Si se deja en blanco, se usará el número por defecto."
    )
    whatsapp_message = models.TextField(
        blank=True, 
        help_text="Mensaje predeterminado de WhatsApp para este servicio. Si se deja en blanco, no habrá mensaje."
    )
    # ---------------------
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Testimonial(models.Model):
    quote = models.TextField(help_text="El texto del testimonio.")
    author = models.CharField(max_length=100, help_text="Ej: 'Paciente de Terapia de Pareja'")
    is_visible = models.BooleanField(default=True, help_text="Marcar para que se muestre en la web.")
    
    def __str__(self):
        return f'Testimonio de {self.author}'

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    content = models.TextField()
    # Imagen principal del artículo del blog
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True, help_text="Imagen destacada para el artículo.", storage=s3_storage)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Mensaje de {self.name} ({self.email})'
        
class SiteSettings(models.Model):
    # Campos que ya teníamos
    default_whatsapp_number = models.CharField(
        max_length=20, 
        blank=True, 
        help_text="El número de WhatsApp principal que se usará en toda la web."
    )
    default_whatsapp_message = models.TextField(
        blank=True, 
        help_text="El mensaje predeterminado de WhatsApp que se usará en toda la web."
    )
    
    # --- CAMPOS NUEVOS PARA REDES SOCIALES ---
    instagram_url = models.URLField(max_length=200, blank=True, help_text="URL completa del perfil de Instagram.")
    facebook_url = models.URLField(max_length=200, blank=True, help_text="URL completa de la página de Facebook.")
    tiktok_url = models.URLField(max_length=200, blank=True, help_text="URL completa del perfil de TikTok.")
    youtube_url = models.URLField(max_length=200, blank=True, help_text="URL completa del canal de YouTube.")
    # -------------------------------------------
    
    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError('Solo puede existir una instancia de SiteSettings.')
        return super(SiteSettings, self).save(*args, **kwargs)

    def __str__(self):
        return "Configuración General del Sitio"

# --- NUEVO MODELO PARA LIBROS ---
class Book(models.Model):
    title = models.CharField(max_length=200, help_text="Título del libro")
    slug = models.SlugField(max_length=200, unique=True, help_text="Versión amigable para URL, ej: mi-libro-digital")
    description = models.TextField(help_text="Descripción o sinopsis del libro.")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio de venta del libro.")
    author = models.CharField(max_length=100, blank=True, help_text="Autor del libro, si no eres tú.")
    
    # Archivos en S3
    cover_image = models.ImageField(upload_to='book_covers/', help_text="Imagen de portada del libro.", storage=s3_storage)
    pdf_file = models.FileField(upload_to='book_pdfs/', help_text="Archivo PDF del libro (se mantendrá privado).", storage=s3_storage)
    
    is_published = models.BooleanField(default=True, help_text="Marcar para que el libro sea visible en la tienda.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
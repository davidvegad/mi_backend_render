from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

s3_storage = S3Boto3Storage()

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='link_profile', null=True, blank=True)
    name = models.CharField(max_length=100)
    bio = models.TextField()
    avatar = models.ImageField(upload_to='avatars/', storage=s3_storage, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)

    # --- Campos de Personalización ---

    # Paso 1: Categorización
    profile_type = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: Creador de Contenido, Artista")
    purpose = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: Profesional, Hobbies")

    # Paso 4: Estilo y Plantilla
    template_style = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: Minimalista, Foto destacada")

    # Paso 5: Tema y Colores
    theme = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: Cielo, Medianoche")
    custom_gradient_start = models.CharField(max_length=7, blank=True, null=True, help_text="Color inicial del degradado, ej: #FFFFFF")
    custom_gradient_end = models.CharField(max_length=7, blank=True, null=True, help_text="Color final del degradado, ej: #000000")
    background_image = models.ImageField(upload_to='backgrounds/', storage=s3_storage, blank=True, null=True)
    background_preference = models.CharField(max_length=10, default='color', help_text="Preferencia de fondo: 'image' o 'color'")
    image_overlay = models.CharField(max_length=10, default='none', help_text="Superposición de imagen: 'none', 'dark', o 'light'")

    # --- Campos de Analíticas ---
    views = models.PositiveIntegerField(default=0)

    # --- Campos de Estilo de Botones ---
    button_style = models.CharField(max_length=20, blank=True, null=True, help_text="Ej: rounded, squared, outline")
    button_color = models.CharField(max_length=7, blank=True, null=True, help_text="Color de fondo del botón, ej: #000000")
    button_text_color = models.CharField(max_length=7, blank=True, null=True, help_text="Color del texto del botón, ej: #FFFFFF")
    button_text_opacity = models.FloatField(default=1.0, help_text="Opacidad del texto del botón (0.0 a 1.0)")
    button_background_opacity = models.FloatField(default=1.0, help_text="Opacidad del fondo del botón (0.0 a 1.0)") # Nuevo
    button_border_color = models.CharField(max_length=7, blank=True, null=True, help_text="Color del borde del botón, ej: #000000") # Nuevo
    button_border_opacity = models.FloatField(default=1.0, help_text="Opacidad del borde del botón (0.0 a 1.0)") # Nuevo
    button_shadow_color = models.CharField(max_length=7, blank=True, null=True, help_text="Color de la sombra del botón, ej: #000000") # Nuevo
    button_shadow_opacity = models.FloatField(default=1.0, help_text="Opacidad de la sombra del botón (0.0 a 1.0)") # Nuevo
    font_family = models.CharField(max_length=100, blank=True, null=True, default='font-inter', help_text="Clase CSS de la fuente seleccionada")

    # --- Campos de Enlaces ---
    

    # --- Campos de Enlaces ---
    

    def __str__(self):
        return self.name

def pre_save_profile_receiver(sender, instance, *args, **kwargs):
    # Generar el slug solo si es una nueva instancia o si el slug está vacío
    if not instance.slug: # Only generate if slug is empty (new instance or explicitly cleared)
        if instance.name: # Ensure name exists to create a slug
            instance.slug = slugify(instance.name)
    
    # Asegurar que el slug sea único
    if instance.slug:
        original_slug = instance.slug
        counter = 1
        while Profile.objects.filter(slug=instance.slug).exclude(pk=instance.pk).exists():
            instance.slug = f"{original_slug}-{counter}"
            counter += 1

pre_save.connect(pre_save_profile_receiver, sender=Profile)

class Link(models.Model):
    LINK_TYPE_CHOICES = [
        ('generic', 'Genérico'),
        ('instagram', 'Instagram'),
        ('whatsapp', 'WhatsApp'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('x', 'X (Twitter)'),
        ('facebook', 'Facebook'),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links')
    title = models.CharField(max_length=100)
    url = models.URLField()
    type = models.CharField(max_length=20, choices=LINK_TYPE_CHOICES, default='generic')
    order = models.PositiveIntegerField(default=0, help_text="Para ordenar los enlaces")
    clicks = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

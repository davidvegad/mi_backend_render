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
    cover_image = models.ImageField(upload_to='covers/', storage=s3_storage, null=True, blank=True)
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

    # --- Campos Avanzados ---
    custom_css = models.TextField(blank=True, default='', help_text="CSS personalizado para el perfil")
    animations = models.JSONField(default=list, blank=True, help_text="Configuración de animaciones del perfil")

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

class SocialIcon(models.Model):
    SOCIAL_TYPES = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter/X'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('github', 'GitHub'),
        ('discord', 'Discord'),
        ('twitch', 'Twitch'),
        ('spotify', 'Spotify'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('snapchat', 'Snapchat'),
        ('pinterest', 'Pinterest'),
        ('behance', 'Behance'),
        ('dribbble', 'Dribbble'),
        ('reddit', 'Reddit'),
        ('email', 'Email'),
        ('website', 'Website'),
        ('other', 'Other'),
    ]
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='social_icons')
    social_type = models.CharField(max_length=20, choices=SOCIAL_TYPES)
    username = models.CharField(max_length=100, help_text="Username o ID de usuario")
    url = models.URLField(help_text="URL completa del perfil social")
    order = models.PositiveIntegerField(default=0, help_text="Orden de aparición")
    
    class Meta:
        ordering = ['order']
        unique_together = ['profile', 'social_type']  # Un solo icono por red social por perfil
    
    def __str__(self):
        return f"{self.profile.name} - {self.get_social_type_display()}"


# ===== MODELOS DE ANALYTICS =====

class ProfileView(models.Model):
    """Registra cada vista a un perfil"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile_views')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True, null=True)
    
    # Información del dispositivo
    device_type = models.CharField(max_length=20, blank=True, choices=[
        ('mobile', 'Mobile'),
        ('desktop', 'Desktop'),
        ('tablet', 'Tablet'),
    ])
    
    # Geolocalización (básica)
    country = models.CharField(max_length=100, blank=True)
    country_code = models.CharField(max_length=2, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['profile', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"Vista a {self.profile.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class LinkClick(models.Model):
    """Registra cada click en un enlace específico"""
    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='link_clicks')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='all_link_clicks')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True, null=True)
    
    # Información del dispositivo
    device_type = models.CharField(max_length=20, blank=True, choices=[
        ('mobile', 'Mobile'),
        ('desktop', 'Desktop'),
        ('tablet', 'Tablet'),
    ])
    
    # Geolocalización (básica)
    country = models.CharField(max_length=100, blank=True)
    country_code = models.CharField(max_length=2, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['link', '-timestamp']),
            models.Index(fields=['profile', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"Click en {self.link.title} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class SocialIconClick(models.Model):
    """Registra cada click en un icono de red social específico"""
    social_icon = models.ForeignKey(SocialIcon, on_delete=models.CASCADE, related_name='social_clicks')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='all_social_clicks')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True, null=True)
    
    # Información del dispositivo
    device_type = models.CharField(max_length=20, blank=True, choices=[
        ('mobile', 'Mobile'),
        ('desktop', 'Desktop'),
        ('tablet', 'Tablet'),
    ])
    
    # Geolocalización (básica)
    country = models.CharField(max_length=100, blank=True)
    country_code = models.CharField(max_length=2, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['social_icon', '-timestamp']),
            models.Index(fields=['profile', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"Click en {self.social_icon.get_social_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class AnalyticsCache(models.Model):
    """Cache para métricas calculadas pesadas"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='analytics_cache')
    cache_key = models.CharField(max_length=100)  # Ej: "device_stats_7d", "geo_stats_30d"
    time_range = models.CharField(max_length=10)  # 7d, 30d, 90d
    data = models.JSONField()  # Datos calculados en formato JSON
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        unique_together = ['profile', 'cache_key', 'time_range']
        indexes = [
            models.Index(fields=['profile', 'cache_key', 'time_range']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Cache {self.cache_key} para {self.profile.name}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

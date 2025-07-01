from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage

# Si tienes una configuración global en settings.py, no necesitas instanciar aquí.
# Pero si quieres ser explícito, puedes hacerlo así.
s3_storage = S3Boto3Storage()

class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    icono = models.CharField(max_length=50)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class Paquete(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion_corta = models.CharField(max_length=255)
    caracteristicas = models.JSONField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.titulo

class ArticuloBlog(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    imagen_destacada = models.ImageField(upload_to='blog_images/', storage=s3_storage)
    fecha_publicacion = models.DateField(auto_now_add=True)
    autor = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=255)

    def __str__(self):
        return self.titulo

class PreguntaFrecuente(models.Model):
    pregunta = models.CharField(max_length=255)
    respuesta = models.TextField()

    def __str__(self):
        return self.pregunta
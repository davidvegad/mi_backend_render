from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage # <-- 1. Importar

s3_storage = S3Boto3Storage()

class Noticia(models.Model):
    titulo = models.CharField(max_length=150)
    resumen = models.TextField()
    cuerpo = models.TextField()
    imagen = models.ImageField(upload_to='noticias/', storage=s3_storage)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class Jugador(models.Model):
    nombre = models.CharField(max_length=100)
    posicion = models.CharField(max_length=50)
    foto = models.ImageField(upload_to='team/', blank=True, null=True, storage=s3_storage)

    def __str__(self):
        return self.nombre


class HeroSlide(models.Model):
    imagen = models.ImageField(upload_to='hero/', storage=s3_storage)
    titulo = models.CharField(max_length=100, blank=True)
    subtitulo = models.CharField(max_length=200, blank=True)
    boton_texto = models.CharField(max_length=50, blank=True)
    link = models.URLField('Enlace destino', blank=True)
    orden = models.PositiveIntegerField(default=0, help_text='Para ordenar los slides')

    def __str__(self):
        return self.titulo or f"Slide {self.pk}"
        
class Partido(models.Model):
    liga = models.CharField(max_length=100, blank=True, null=True)
    equipo_rival = models.CharField(max_length=100)
    fecha = models.DateField()
    hora = models.TimeField()
    lugar = models.CharField(max_length=100)
    logo_visitante = models.ImageField(upload_to='logos_visitantes/', blank=True, null=True, storage=s3_storage)
    goles_local = models.PositiveSmallIntegerField("Goles Tumbes FC", default=0)
    goles_visitante = models.PositiveSmallIntegerField("Goles rival", default=0)
    goleadores_local = models.CharField("Goleadores Tumbes FC", max_length=250, blank=True)
    goleadores_visitante = models.CharField("Goleadores rival", max_length=250, blank=True)
    finalizado = models.BooleanField("¿Ya jugado?", default=False)

    def __str__(self):
        return f"{self.liga or ''}: Tumbes FC {self.goles_local or ''} - {self.goles_visitante or ''} {self.equipo_rival}"
        
class Sponsor(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='sponsors/', storage=s3_storage)
    url = models.URLField('Sitio web o red social')
    destacado = models.BooleanField('¿Sponsor influyente?', default=False)

    def __str__(self):
        return self.nombre

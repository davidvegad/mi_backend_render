# Generated by Django 5.2.3 on 2025-07-07 00:42

import storages.backends.s3
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0006_remove_profile_facebook_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='background_image',
            field=models.ImageField(blank=True, null=True, storage=storages.backends.s3.S3Storage(), upload_to='backgrounds/'),
        ),
        migrations.AddField(
            model_name='profile',
            name='custom_gradient_end',
            field=models.CharField(blank=True, help_text='Color final del degradado, ej: #000000', max_length=7, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='custom_gradient_start',
            field=models.CharField(blank=True, help_text='Color inicial del degradado, ej: #FFFFFF', max_length=7, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='profile_type',
            field=models.CharField(blank=True, help_text='Ej: Creador de Contenido, Artista', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='purpose',
            field=models.CharField(blank=True, help_text='Ej: Profesional, Hobbies', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='template_style',
            field=models.CharField(blank=True, help_text='Ej: Minimalista, Foto destacada', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='theme',
            field=models.CharField(blank=True, help_text='Ej: Cielo, Medianoche', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, storage=storages.backends.s3.S3Storage(), upload_to='avatars/'),
        ),
    ]

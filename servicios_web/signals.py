
import requests
import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ArticuloBlog

@receiver([post_save, post_delete], sender=ArticuloBlog)
def trigger_render_build(sender, instance, **kwargs):
    """
    Dispara un build en Render cada vez que un artículo del blog se crea,
    actualiza o elimina.
    """
    hook_url = os.getenv('RENDER_BUILD_HOOK_URL')
    if hook_url:
        try:
            print(f"Disparando build en Render para el artículo: {instance.titulo}")
            response = requests.post(hook_url)
            response.raise_for_status()  # Lanza un error si la petición falla
            print("Build hook disparado exitosamente.")
        except requests.exceptions.RequestException as e:
            # Aquí podrías añadir un logging más robusto
            print(f"Error al disparar el build hook: {e}")
    else:
        print("RENDER_BUILD_HOOK_URL no está configurada. No se disparará el build.")

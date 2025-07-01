from django.apps import AppConfig


class ServiciosWebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'servicios_web'

    def ready(self):
        import servicios_web.signals

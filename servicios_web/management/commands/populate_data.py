from django.core.management.base import BaseCommand
from servicios_web.models import Servicio, Paquete, ArticuloBlog, PreguntaFrecuente
import datetime

class Command(BaseCommand):
    help = 'Populates the database with sample data for Servicios Web.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Populating database with sample data...'))

        # Clear existing data (optional, for fresh runs)
        Servicio.objects.all().delete()
        Paquete.objects.all().delete()
        ArticuloBlog.objects.all().delete()
        PreguntaFrecuente.objects.all().delete()

        # Create Servicios
        servicios_data = [
            {"nombre": "Diseño de Páginas Web", "icono": "fas fa-desktop", "descripcion": "Creamos diseños web atractivos y funcionales que capturan la esencia de tu marca."},
            {"nombre": "Tiendas en Línea (E-commerce)", "icono": "fas fa-shopping-cart", "descripcion": "Desarrollamos plataformas de comercio electrónico robustas y seguras para que vendas tus productos online."}, 
            {"nombre": "Creación de Contenido", "icono": "fas fa-pencil-alt", "descripcion": "Generamos contenido relevante y de calidad para tu sitio web y redes sociales."}, 
            {"nombre": "Desarrollo Web a Medida", "icono": "fas fa-code", "descripcion": "Construimos soluciones web personalizadas que se adaptan perfectamente a tus necesidades específicas."}, 
            {"nombre": "Optimización SEO", "icono": "fas fa-search", "descripcion": "Mejoramos la visibilidad de tu sitio web en los motores de búsqueda para atraer más tráfico orgánico."}, 
            {"nombre": "Seguridad y Mantenimiento", "icono": "fas fa-shield-alt", "descripcion": "Aseguramos y mantenemos tu sitio web actualizado, protegiéndolo de amenazas y garantizando su óptimo rendimiento."},
        ]
        for data in servicios_data:
            Servicio.objects.create(**data)
        self.stdout.write(self.style.SUCCESS(f'Created {len(servicios_data)} Servicios.'))

        # Create Paquetes
        paquetes_data = [
            {
                "titulo": "Paquete Básico Emprendedor",
                "descripcion_corta": "Ideal para iniciar tu presencia online.",
                "caracteristicas": ["Diseño Web Básico", "Dominio y Hosting (1 año)", "Integración de Redes Sociales", "Formulario de Contacto"],
                "precio": 499.99
            },
            {
                "titulo": "Paquete PYME Pro",
                "descripcion_corta": "Solución completa para pequeñas y medianas empresas.",
                "caracteristicas": ["Diseño Web Avanzado", "Tienda Online (hasta 50 productos)", "SEO Básico", "Soporte Prioritario"],
                "precio": 999.99
            },
            {
                "titulo": "Paquete Corporativo Premium",
                "descripcion_corta": "Para empresas consolidadas que buscan escalar.",
                "caracteristicas": ["Diseño Web Personalizado", "E-commerce Avanzado (productos ilimitados)", "SEO Estratégico", "Mantenimiento Mensual", "Integración CRM"],
                "precio": 1999.99
            },
            {
                "titulo": "Paquete Agencia Colaboración",
                "descripcion_corta": "Diseñado para agencias y equipos creativos.",
                "caracteristicas": ["Desarrollo a Medida", "Integración de APIs", "Soporte Dedicado", "Consultoría Técnica"],
                "precio": 2500.00
            },
        ]
        for data in paquetes_data:
            Paquete.objects.create(**data)
        self.stdout.write(self.style.SUCCESS(f'Created {len(paquetes_data)} Paquetes.'))

        # Create ArticulosBlog
        blog_data = [
            {
                "titulo": "Las 5 Claves para un Diseño Web Exitoso",
                "contenido": "Un buen diseño web es crucial para tu negocio. Aquí te presentamos las 5 claves...",
                "imagen_destacada": "blog_images/diseno_web.jpg",
                "autor": "Equipo Servicios Web",
                "slug": "5-claves-diseno-web-exitoso"
            },
            {
                "titulo": "Cómo el SEO puede Transformar tu Negocio",
                "contenido": "El SEO no es solo para grandes empresas. Descubre cómo puede ayudarte...",
                "imagen_destacada": "blog_images/seo_negocio.jpg",
                "autor": "Equipo Servicios Web",
                "slug": "seo-transformar-negocio"
            },
        ]
        for data in blog_data:
            ArticuloBlog.objects.create(**data)
        self.stdout.write(self.style.SUCCESS(f'Created {len(blog_data)} ArticulosBlog.'))

        # Create PreguntasFrecuentes
        faq_data = [
            {"pregunta": "¿Cuánto tiempo tarda en desarrollarse una página web?", "respuesta": "El tiempo de desarrollo varía según la complejidad del proyecto, pero un sitio web básico puede estar listo en 2-4 semanas."}, 
            {"pregunta": "¿Ofrecen servicios de mantenimiento post-lanzamiento?", "respuesta": "Sí, ofrecemos planes de mantenimiento y soporte para asegurar que tu sitio web funcione siempre a la perfección."}, 
            {"pregunta": "¿Puedo actualizar el contenido de mi sitio web yo mismo?", "respuesta": "Sí, la mayoría de nuestros proyectos incluyen un sistema de gestión de contenido (CMS) fácil de usar para que puedas actualizar tu sitio sin conocimientos técnicos."}, 
        ]
        for data in faq_data:
            PreguntaFrecuente.objects.create(**data)
        self.stdout.write(self.style.SUCCESS(f'Created {len(faq_data)} PreguntasFrecuentes.'))

        self.stdout.write(self.style.SUCCESS('Database population complete!'))

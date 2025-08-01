# Comando para crear datos de ejemplo del sistema de evaluación
from django.core.management.base import BaseCommand
from timehub.models_evaluation import ObjectiveCategory, EvaluationRole, Objective, Quarter
from datetime import date


class Command(BaseCommand):
    help = 'Crea datos de ejemplo para el sistema de evaluación trimestral'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de ejemplo del sistema de evaluación...')
        
        # Crear categorías de objetivos
        categories_data = [
            {
                'name': 'TECHNICAL',
                'display_name': 'Desempeño Técnico',
                'description': 'Objetivos relacionados con habilidades técnicas, calidad del código, y dominio de herramientas',
                'order': 1
            },
            {
                'name': 'COLLABORATION',
                'display_name': 'Colaboración y Equipo',
                'description': 'Objetivos relacionados con trabajo en equipo, comunicación y liderazgo',
                'order': 2
            },
            {
                'name': 'GROWTH',
                'display_name': 'Formación - Crecimiento',
                'description': 'Objetivos relacionados con aprendizaje continuo, capacitación y desarrollo profesional',
                'order': 3
            }
        ]
        
        for cat_data in categories_data:
            category, created = ObjectiveCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'display_name': cat_data['display_name'],
                    'description': cat_data['description'],
                    'order': cat_data['order']
                }
            )
            if created:
                self.stdout.write(f'✅ Creada categoría: {category.display_name}')
            else:
                self.stdout.write(f'ℹ️  Categoría ya existe: {category.display_name}')
        
        # Crear roles de ejemplo
        roles_data = [
            {
                'name': 'Desarrollador Junior',
                'description': 'Desarrollador con 0-2 años de experiencia'
            },
            {
                'name': 'Desarrollador Semi-Senior',
                'description': 'Desarrollador con 2-4 años de experiencia'
            },
            {
                'name': 'Desarrollador Senior',
                'description': 'Desarrollador con 4+ años de experiencia'
            },
            {
                'name': 'Tech Lead',
                'description': 'Líder técnico de equipo'
            },
            {
                'name': 'Project Manager',
                'description': 'Gerente de proyectos'
            },
            {
                'name': 'QA Analyst',
                'description': 'Analista de calidad y testing'
            }
        ]
        
        for role_data in roles_data:
            role, created = EvaluationRole.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created:
                self.stdout.write(f'✅ Creado rol: {role.name}')
            else:
                self.stdout.write(f'ℹ️  Rol ya existe: {role.name}')
        
        # Crear trimestres para 2024 y 2025
        quarters_data = [
            # 2024
            {'year': 2024, 'quarter': 'Q1', 'start_date': '2024-01-01', 'end_date': '2024-03-31', 'is_active': False},
            {'year': 2024, 'quarter': 'Q2', 'start_date': '2024-04-01', 'end_date': '2024-06-30', 'is_active': False},
            {'year': 2024, 'quarter': 'Q3', 'start_date': '2024-07-01', 'end_date': '2024-09-30', 'is_active': False},
            {'year': 2024, 'quarter': 'Q4', 'start_date': '2024-10-01', 'end_date': '2024-12-31', 'is_active': False},
            
            # 2025
            {'year': 2025, 'quarter': 'Q1', 'start_date': '2025-01-01', 'end_date': '2025-03-31', 'is_active': True},
            {'year': 2025, 'quarter': 'Q2', 'start_date': '2025-04-01', 'end_date': '2025-06-30', 'is_active': False},
            {'year': 2025, 'quarter': 'Q3', 'start_date': '2025-07-01', 'end_date': '2025-09-30', 'is_active': False},
            {'year': 2025, 'quarter': 'Q4', 'start_date': '2025-10-01', 'end_date': '2025-12-31', 'is_active': False},
        ]
        
        for quarter_data in quarters_data:
            quarter, created = Quarter.objects.get_or_create(
                year=quarter_data['year'],
                quarter=quarter_data['quarter'],
                defaults={
                    'start_date': quarter_data['start_date'],
                    'end_date': quarter_data['end_date'],
                    'is_active': quarter_data['is_active']
                }
            )
            if created:
                self.stdout.write(f'✅ Creado trimestre: {quarter.quarter_display} {quarter.year}')
            else:
                self.stdout.write(f'ℹ️  Trimestre ya existe: {quarter.quarter_display} {quarter.year}')
        
        # Crear objetivos de ejemplo para Desarrollador Senior
        try:
            dev_senior_role = EvaluationRole.objects.get(name='Desarrollador Senior')
            technical_cat = ObjectiveCategory.objects.get(name='TECHNICAL')
            collaboration_cat = ObjectiveCategory.objects.get(name='COLLABORATION')
            growth_cat = ObjectiveCategory.objects.get(name='GROWTH')
            
            objectives_data = [
                # Objetivos Técnicos
                {
                    'role': dev_senior_role,
                    'category': technical_cat,
                    'title': 'Calidad del Código',
                    'description': 'Mantener un código limpio, bien documentado y siguiendo las mejores prácticas. Reducir la cantidad de bugs reportados en un 20%.',
                    'weight': 2.0
                },
                {
                    'role': dev_senior_role,
                    'category': technical_cat,
                    'title': 'Arquitectura y Diseño',
                    'description': 'Proponer y implementar mejoras en la arquitectura de al menos 2 proyectos, documentando las decisiones técnicas.',
                    'weight': 2.0
                },
                {
                    'role': dev_senior_role,
                    'category': technical_cat,
                    'title': 'Performance y Optimización',
                    'description': 'Identificar y resolver cuellos de botella, mejorando el rendimiento de aplicaciones críticas en un 15%.',
                    'weight': 1.5
                },
                
                # Objetivos de Colaboración
                {
                    'role': dev_senior_role,
                    'category': collaboration_cat,
                    'title': 'Mentoría a Desarrolladores Junior',
                    'description': 'Guiar y mentorar a al menos 2 desarrolladores junior, realizando code reviews regulares y sesiones de capacitación.',
                    'weight': 2.0
                },
                {
                    'role': dev_senior_role,
                    'category': collaboration_cat,
                    'title': 'Participación en Reuniones Técnicas',
                    'description': 'Participar activamente en reuniones de planificación, retrospectivas y sesiones de arquitectura, aportando soluciones constructivas.',
                    'weight': 1.5
                },
                {
                    'role': dev_senior_role,
                    'category': collaboration_cat,
                    'title': 'Comunicación con Stakeholders',
                    'description': 'Comunicar efectivamente el progreso técnico y posibles riesgos a project managers y clientes.',
                    'weight': 1.5
                },
                
                # Objetivos de Crecimiento
                {
                    'role': dev_senior_role,
                    'category': growth_cat,
                    'title': 'Capacitación Técnica Continua',
                    'description': 'Completar al menos 2 cursos o certificaciones relevantes para el stack tecnológico del equipo.',
                    'weight': 1.5
                },
                {
                    'role': dev_senior_role,
                    'category': growth_cat,
                    'title': 'Contribución a la Comunidad',
                    'description': 'Realizar al menos 3 presentaciones internas sobre nuevas tecnologías o mejores prácticas.',
                    'weight': 1.0
                },
                {
                    'role': dev_senior_role,
                    'category': growth_cat,
                    'title': 'Innovación y Mejora Continua',
                    'description': 'Proponer e implementar al menos 2 mejoras en procesos de desarrollo o herramientas del equipo.',
                    'weight': 1.5
                }
            ]
            
            for obj_data in objectives_data:
                objective, created = Objective.objects.get_or_create(
                    role=obj_data['role'],
                    category=obj_data['category'],
                    title=obj_data['title'],
                    defaults={
                        'description': obj_data['description'],
                        'weight': obj_data['weight']
                    }
                )
                if created:
                    self.stdout.write(f'✅ Creado objetivo: {objective.title}')
                else:
                    self.stdout.write(f'ℹ️  Objetivo ya existe: {objective.title}')
                    
        except EvaluationRole.DoesNotExist:
            self.stdout.write('⚠️  No se encontró el rol "Desarrollador Senior", objetivos no creados')
        except ObjectiveCategory.DoesNotExist:
            self.stdout.write('⚠️  No se encontraron las categorías, objetivos no creados')
        
        self.stdout.write(self.style.SUCCESS('✅ Datos de ejemplo creados exitosamente!'))
        self.stdout.write('')
        self.stdout.write('Datos creados:')
        self.stdout.write(f'- {ObjectiveCategory.objects.count()} categorías de objetivos')
        self.stdout.write(f'- {EvaluationRole.objects.count()} roles de evaluación')
        self.stdout.write(f'- {Quarter.objects.count()} trimestres')
        self.stdout.write(f'- {Objective.objects.count()} objetivos de ejemplo')
        self.stdout.write('')
        self.stdout.write('El sistema está listo para usar!')
        self.stdout.write('Trimestre activo: Q1 2025')
# Filtros personalizados para templates de evaluación
from django import template

register = template.Library()

@register.filter
def filter_by_category(objectives, category):
    """Filtro para obtener objetivos por categoría"""
    return [obj for obj in objectives if obj.objective.category.name == category]
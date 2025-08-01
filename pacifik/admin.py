from django.contrib import admin
from .models import Area, UserProfile, Reserva


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cupos_por_horario', 'activa', 'created_at']
    list_filter = ['activa', 'created_at']
    search_fields = ['nombre']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'instrucciones', 'cupos_por_horario', 'activa')
        }),
        ('Configuración de Horarios', {
            'fields': ('horarios_permitidos', 'duraciones_permitidas')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'numero_departamento', 'es_administrador', 'created_at']
    list_filter = ['es_administrador', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'numero_departamento']
    readonly_fields = ['created_at']


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'area', 'fecha', 'horario_inicio', 'horario_fin', 'estado', 'created_at']
    list_filter = ['estado', 'area', 'fecha', 'created_at']
    search_fields = ['usuario__email', 'usuario__first_name', 'usuario__last_name', 'area__nombre']
    readonly_fields = ['created_at', 'updated_at', 'duracion_horas']
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información de la Reserva', {
            'fields': ('usuario', 'area', 'fecha', 'horario_inicio', 'horario_fin')
        }),
        ('Estado y Términos', {
            'fields': ('estado', 'terminos_aceptados')
        }),
        ('Información Adicional', {
            'fields': ('duracion_horas',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario', 'area')

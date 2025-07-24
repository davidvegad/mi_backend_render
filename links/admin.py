from django.contrib import admin
from .models import Profile, Link, SocialIcon, ProfileView, LinkClick, SocialIconClick, AnalyticsCache

# ===== MODELOS PRINCIPALES =====

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'user', 'views', 'theme', 'created_at')
    list_filter = ('theme', 'background_preference', 'button_style')
    search_fields = ('name', 'slug', 'bio', 'user__username', 'user__email')
    readonly_fields = ('slug', 'views')
    
    def created_at(self, obj):
        return obj.user.date_joined if obj.user else None
    created_at.short_description = 'Created'

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'type', 'clicks', 'order', 'url_preview')
    list_filter = ('type', 'profile__name')
    search_fields = ('title', 'url', 'profile__name')
    ordering = ('profile', 'order')
    
    def url_preview(self, obj):
        return obj.url[:50] + '...' if len(obj.url) > 50 else obj.url
    url_preview.short_description = 'URL'

@admin.register(SocialIcon)
class SocialIconAdmin(admin.ModelAdmin):
    list_display = ('profile', 'social_type', 'username', 'order')
    list_filter = ('social_type',)
    search_fields = ('profile__name', 'username', 'url')
    ordering = ('profile', 'order')


# ===== MODELOS DE ANALYTICS =====

@admin.register(ProfileView)
class ProfileViewAdmin(admin.ModelAdmin):
    list_display = ('profile', 'timestamp', 'device_type', 'country', 'ip_address')
    list_filter = ('device_type', 'country', 'timestamp')
    search_fields = ('profile__name', 'country', 'ip_address')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False  # No permitir crear manualmente
    
    def has_change_permission(self, request, obj=None):
        return False  # Solo lectura

@admin.register(LinkClick)
class LinkClickAdmin(admin.ModelAdmin):
    list_display = ('link', 'profile', 'timestamp', 'device_type', 'country', 'ip_address')
    list_filter = ('device_type', 'country', 'timestamp', 'link__type')
    search_fields = ('link__title', 'profile__name', 'country', 'ip_address')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False  # No permitir crear manualmente
    
    def has_change_permission(self, request, obj=None):
        return False  # Solo lectura

@admin.register(SocialIconClick)
class SocialIconClickAdmin(admin.ModelAdmin):
    list_display = ('social_icon', 'profile', 'timestamp', 'device_type', 'country', 'ip_address')
    list_filter = ('social_icon__social_type', 'device_type', 'country', 'timestamp')
    search_fields = ('profile__name', 'social_icon__social_type', 'ip_address')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False  # No permitir crear manualmente
    
    def has_change_permission(self, request, obj=None):
        return False  # Solo lectura

@admin.register(AnalyticsCache)
class AnalyticsCacheAdmin(admin.ModelAdmin):
    list_display = ('profile', 'cache_key', 'time_range', 'created_at', 'expires_at', 'is_expired')
    list_filter = ('time_range', 'created_at', 'expires_at')
    search_fields = ('profile__name', 'cache_key')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'is_expired')
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


# ===== CONFIGURACIÓN DEL ADMIN SITE =====

admin.site.site_header = 'EnlacePro Admin'
admin.site.site_title = 'EnlacePro Admin'
admin.site.index_title = 'Panel de Administración'

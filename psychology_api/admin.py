# psychology_api/admin.py

from django.contrib import admin
from .models import Profile, Service, Testimonial, Post, ContactSubmission, SiteSettings 

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'slug')
    prepopulated_fields = {'slug': ('title',)}

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'author', 'created_at')
    list_filter = ('status', 'author')
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Profile)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Testimonial)
admin.site.register(Post, PostAdmin)
admin.site.register(ContactSubmission)
admin.site.register(SiteSettings)
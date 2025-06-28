# psychology_api/serializers.py

from rest_framework import serializers
from .models import Profile, Service, Testimonial, Post, ContactSubmission, SiteSettings
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    photo_url = serializers.ImageField(source='photo', read_only=True) # Devuelve la URL de la imagen

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'philosophy', 'photo_url', 'professional_id']

class ServiceSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='image', read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'title', 'slug', 'description', 'image_url', 'whatsapp_number', 'whatsapp_message']

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'quote', 'author']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    featured_image_url = serializers.ImageField(source='featured_image', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'author', 'content', 'featured_image_url', 'created_at', 'status']

class ContactSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = ['id', 'name', 'email', 'message']
        
class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        # Añadimos los nuevos campos a la lista
        fields = [
            'default_whatsapp_number', 
            'default_whatsapp_message',
            'instagram_url',
            'facebook_url',
            'tiktok_url',
            'youtube_url'
        ]        
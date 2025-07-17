from django.contrib.auth import authenticate
import json
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.http import QueryDict
from rest_framework.parsers import JSONParser
from io import BytesIO
from .models import Profile, Link, SocialIcon

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')

    def validate_email(self, value):
        # Check if a user with this email already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'], # Usar el email como username de Django
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email' # Especificamos que el campo de usuario es el email
    email = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminamos el campo 'username' que se añade por defecto
        if 'username' in self.fields:
            self.fields.pop('username')

    def validate(self, attrs):
        data = super().validate(attrs)

        # Si la autenticación fue exitosa, self.user estará establecido
        if not self.user.is_active:
            raise serializers.ValidationError("La cuenta de usuario está inactiva.")

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['name'] = user.first_name + " " + user.last_name if user.first_name and user.last_name else user.username
        token['email'] = user.email
        return token


class LinkSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # Allow ID for updates

    class Meta:
        model = Link
        fields = ('id', 'title', 'url', 'type', 'order')
        # El campo 'type' ahora es gestionado por el cliente.

class SocialIconSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # Allow ID for updates

    class Meta:
        model = SocialIcon
        fields = ('id', 'social_type', 'username', 'url', 'order')

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    links = LinkSerializer(many=True, required=False)
    social_icons = SocialIconSerializer(many=True, required=False)

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'name', 'bio', 'avatar', 'cover_image', 'slug', 
            'profile_type', 'purpose', 'template_style', 'theme', 
            'custom_gradient_start', 'custom_gradient_end', 'background_image',
            'background_preference', 'image_overlay',
            'button_style', 'button_color', 'button_text_color', 'button_text_opacity',
            'button_background_opacity', 'button_border_color', 'button_border_opacity',
            'button_shadow_color', 'button_shadow_opacity', 'font_family',
            'links', 'social_icons'
        )
        read_only_fields = ('id', 'user')
        
    def update(self, instance, validated_data):
        # Extract links and social_icons data directly from request.data if present
        request_data = self.context['request'].data
        links_data_raw = request_data.get('links', None)
        social_icons_data_raw = request_data.get('social_icons', None)

        # Remove 'links' and 'social_icons' from validated_data to prevent default handling
        validated_data.pop('links', None)
        validated_data.pop('social_icons', None)

        # Update parent instance fields
        instance = super().update(instance, validated_data)

        # Handle nested links
        if links_data_raw is not None:
            # If links_data_raw is a string (from FormData), parse it
            if isinstance(links_data_raw, str):
                try:
                    links_data = json.loads(links_data_raw)
                except json.JSONDecodeError:
                    raise serializers.ValidationError({'links': 'Invalid JSON format.'})
            else:
                # If it's already parsed (e.g., from JSON request body), use it directly
                links_data = links_data_raw

            # Ensure links_data is a list
            if not isinstance(links_data, list):
                raise serializers.ValidationError({'links': 'Expected a list of links.'})

            # Get existing links for the profile
            existing_links = {link.id: link for link in instance.links.all()}
            
            # Process incoming links
            for link_data in links_data:
                link_id = link_data.get('id')
                if link_id and link_id in existing_links:
                    # Update existing link
                    link = existing_links.pop(link_id) # Remove from existing_links to track deletions
                    for attr, value in link_data.items():
                        setattr(link, attr, value)
                    link.save()
                else:
                    # Create new link
                    Link.objects.create(profile=instance, **link_data)
            
            # Delete remaining existing links (those not in incoming_link_ids) if any
            for link_id, link in existing_links.items():
                link.delete()

        # Handle nested social_icons
        if social_icons_data_raw is not None:
            # If social_icons_data_raw is a string (from FormData), parse it
            if isinstance(social_icons_data_raw, str):
                try:
                    social_icons_data = json.loads(social_icons_data_raw)
                except json.JSONDecodeError:
                    raise serializers.ValidationError({'social_icons': 'Invalid JSON format.'})
            else:
                # If it's already parsed (e.g., from JSON request body), use it directly
                social_icons_data = social_icons_data_raw

            # Ensure social_icons_data is a list
            if not isinstance(social_icons_data, list):
                raise serializers.ValidationError({'social_icons': 'Expected a list of social icons.'})

            # Get existing social icons for the profile
            existing_social_icons = {icon.id: icon for icon in instance.social_icons.all()}
            
            # Process incoming social icons
            for icon_data in social_icons_data:
                icon_id = icon_data.get('id')
                if icon_id and icon_id in existing_social_icons:
                    # Update existing social icon
                    icon = existing_social_icons.pop(icon_id) # Remove from existing_social_icons to track deletions
                    for attr, value in icon_data.items():
                        setattr(icon, attr, value)
                    icon.save()
                else:
                    # Create new social icon
                    SocialIcon.objects.create(profile=instance, **icon_data)
            
            # Delete remaining existing social icons (those not in incoming_social_icon_ids) if any
            for icon_id, icon in existing_social_icons.items():
                icon.delete()

        return instance

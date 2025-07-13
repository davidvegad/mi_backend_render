import requests
import os
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Profile, Link
from .serializers import ProfileSerializer, LinkSerializer, UserRegistrationSerializer, CustomTokenObtainPairSerializer
from django.shortcuts import get_object_or_404, redirect

# Vista de prueba
class TestView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response({"message": "¡La vista de prueba de links funciona!"}, status=status.HTTP_200_OK)

class AllProfileSlugsView(APIView):
    permission_classes = [permissions.AllowAny] # No authentication needed

    def get(self, request, *args, **kwargs):
        slugs = Profile.objects.values_list('slug', flat=True)
        return Response(list(slugs))

class ProfileViewTracker(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, slug, *args, **kwargs):
        profile = get_object_or_404(Profile, slug=slug)
        profile.views += 1
        profile.save()
        return Response({'status': 'view tracked'}, status=status.HTTP_200_OK)

class LinkClickTracker(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, link_id, *args, **kwargs):
        link = get_object_or_404(Link, id=link_id)
        link.clicks += 1
        link.save()
        return redirect(link.url)

class AnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        total_views = profile.views
        total_clicks = sum(link.clicks for link in profile.links.all())

        links_data = []
        for link in profile.links.all().order_by('-clicks'):
            links_data.append({
                'id': link.id,
                'title': link.title,
                'url': link.url,
                'clicks': link.clicks,
            })

        return Response({
            'total_views': total_views,
            'total_clicks': total_clicks,
            'links_data': links_data,
        }, status=status.HTTP_200_OK)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        print("¡Solicitud POST recibida en CustomTokenObtainPairView!")
        return super().post(request, *args, **kwargs)

class UserRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile = Profile.objects.create(user=user, name=user.username, bio="")

            # Trigger Render build hook for frontend
            render_build_hook_url = os.getenv('RENDER_BUILD_HOOK_URL')
            if render_build_hook_url:
                try:
                    requests.post(render_build_hook_url)
                    print(f"Render build hook triggered for {profile.slug}")
                except requests.exceptions.RequestException as e:
                    print(f"Error triggering Render build hook: {e}")
            else:
                print("RENDER_BUILD_HOOK_URL not set. Skipping build trigger.")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Profile.objects.filter(user=self.request.user)
        return Profile.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        try:
            profile = self.get_queryset().get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'detail': 'Profile not found for this user.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)

class LinkViewSet(viewsets.ModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Link.objects.filter(profile__user=self.request.user)
        return Link.objects.none()

    def perform_create(self, serializer):
        profile = Profile.objects.get(user=self.request.user)
        serializer.save(profile=profile)

    @action(detail=False, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def reorder(self, request):
        # Expects a list of {id: link_id, order: new_order} objects
        reorder_data = request.data
        if not isinstance(reorder_data, list):
            return Response({'detail': 'Expected a list of link objects.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the profile of the authenticated user
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        for item in reorder_data:
            link_id = item.get('id')
            new_order = item.get('order')

            if link_id is None or new_order is None:
                return Response({'detail': 'Each item must have an id and an order.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Ensure the link belongs to the user's profile
                link = Link.objects.get(id=link_id, profile=profile)
                link.order = new_order
                link.save()
            except Link.DoesNotExist:
                return Response({'detail': f'Link with id {link_id} not found or does not belong to user.'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'detail': 'Links reordered successfully.'}, status=status.HTTP_200_OK)

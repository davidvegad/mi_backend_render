from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ProfileViewSet, LinkViewSet, UserRegisterView, TestView, AllProfileSlugsView, ProfileViewTracker, LinkClickTracker, AnalyticsView

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet)
router.register(r'links', LinkViewSet)

urlpatterns = [
    path('test/', TestView.as_view(), name='test_view'), # Ruta de prueba
    path('register/', UserRegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profiles/slugs/', AllProfileSlugsView.as_view(), name='all_profile_slugs'),
    path('profile-views/<str:slug>/', ProfileViewTracker.as_view(), name='profile_view_tracker'),
    path('link-clicks/<int:link_id>/', LinkClickTracker.as_view(), name='link_click_tracker'),
    path('profiles/me/analytics/', AnalyticsView.as_view(), name='profile_analytics'),
    path('', include(router.urls)),
]

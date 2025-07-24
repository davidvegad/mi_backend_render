from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    ProfileViewSet, LinkViewSet, UserRegisterView, TestView, AllProfileSlugsView, 
    ProfileViewTracker, LinkClickTracker, AnalyticsView, AnalyticsDetailedView,
    DeviceAnalyticsView, GeographyAnalyticsView, DailyClicksAnalyticsView, RecentActivityView,
    RealTimeMetricsView, SocialMediaStatsView, SocialIconClickTracker
)

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
    
    # Analytics endpoints
    path('profiles/me/analytics/', AnalyticsView.as_view(), name='profile_analytics'),
    path('analytics/detailed/', AnalyticsDetailedView.as_view(), name='analytics_detailed'),
    path('analytics/devices/', DeviceAnalyticsView.as_view(), name='analytics_devices'),
    path('analytics/geography/', GeographyAnalyticsView.as_view(), name='analytics_geography'),
    path('analytics/daily/', DailyClicksAnalyticsView.as_view(), name='analytics_daily'),
    path('analytics/recent-activity/', RecentActivityView.as_view(), name='analytics_recent_activity'),
    path('analytics/realtime/', RealTimeMetricsView.as_view(), name='analytics_realtime'),
    path('analytics/social-media/', SocialMediaStatsView.as_view(), name='analytics_social_media'),
    path('social-click/<int:social_icon_id>/', SocialIconClickTracker.as_view(), name='social_icon_click_tracker'),
    
    path('', include(router.urls)),
]

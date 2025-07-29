from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    TimehubTokenObtainPairView,
    ClientViewSet, ProjectViewSet, AssignmentViewSet, 
    PeriodViewSet, TimeEntryViewSet, LeaveTypeViewSet, 
    LeaveRequestViewSet, PlannedAllocationViewSet, MeetingViewSet,
    UserProfileViewSet, HolidayViewSet, AuditLogViewSet, UserViewSet,
    LeaveBalanceViewSet, LeaveCalendarViewSet, ProjectAssignmentViewSet,
    CountryViewSet, RoleViewSet
)

app_name = 'timehub'

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'periods', PeriodViewSet)
router.register(r'time-entries', TimeEntryViewSet)
router.register(r'leave-types', LeaveTypeViewSet)
router.register(r'leave-requests', LeaveRequestViewSet)
router.register(r'planned-allocations', PlannedAllocationViewSet)
router.register(r'meetings', MeetingViewSet)
router.register(r'user-profiles', UserProfileViewSet)
router.register(r'holidays', HolidayViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'users', UserViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'leave-balance', LeaveBalanceViewSet, basename='leave-balance')
router.register(r'leave-calendar', LeaveCalendarViewSet, basename='leave-calendar') 
router.register(r'project-assignments', ProjectAssignmentViewSet, basename='project-assignments')

urlpatterns = [
    # Auth endpoints
    path('v1/auth/token/', TimehubTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints
    path('v1/', include(router.urls)),
]
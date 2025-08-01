# URLs para el sistema de evaluación trimestral
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_evaluation import (
    EvaluationRoleViewSet, ObjectiveCategoryViewSet, ObjectiveViewSet,
    QuarterViewSet, EmployeeEvaluationViewSet, EvaluationObjectiveViewSet,
    EvaluationAttachmentViewSet, UsersViewSet
)

# Router para las APIs del sistema de evaluación
evaluation_router = DefaultRouter()
evaluation_router.register(r'roles', EvaluationRoleViewSet, basename='evaluation-roles')
evaluation_router.register(r'categories', ObjectiveCategoryViewSet, basename='objective-categories')
evaluation_router.register(r'objectives', ObjectiveViewSet, basename='objectives')
evaluation_router.register(r'quarters', QuarterViewSet, basename='quarters')
evaluation_router.register(r'evaluations', EmployeeEvaluationViewSet, basename='employee-evaluations')
evaluation_router.register(r'evaluation-objectives', EvaluationObjectiveViewSet, basename='evaluation-objectives')
evaluation_router.register(r'attachments', EvaluationAttachmentViewSet, basename='evaluation-attachments')
evaluation_router.register(r'users', UsersViewSet, basename='evaluation-users')

urlpatterns = [
    path('evaluation/', include(evaluation_router.urls)),
]
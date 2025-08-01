# Serializers para el sistema de evaluación trimestral
from rest_framework import serializers
from django.contrib.auth.models import User
from .models_evaluation import (
    EvaluationRole, ObjectiveCategory, Objective, Quarter, 
    EmployeeEvaluation, EvaluationObjective, EvaluationAttachment
)


class EvaluationRoleSerializer(serializers.ModelSerializer):
    objectives_count = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationRole
        fields = ['id', 'name', 'description', 'is_active', 'objectives_count', 'created_at', 'updated_at']
        
    def get_objectives_count(self, obj):
        return obj.objective_set.filter(is_active=True).count()


class ObjectiveCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectiveCategory
        fields = ['id', 'name', 'display_name', 'description', 'order']


class ObjectiveSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    category_name = serializers.CharField(source='category.display_name', read_only=True)
    category_code = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Objective
        fields = [
            'id', 'role', 'role_name', 'category', 'category_name', 'category_code',
            'title', 'description', 'weight', 'is_active', 'created_at', 'updated_at'
        ]


class ObjectivesByRoleSerializer(serializers.ModelSerializer):
    """Serializer para mostrar objetivos agrupados por categoría para un rol específico"""
    technical_objectives = serializers.SerializerMethodField()
    collaboration_objectives = serializers.SerializerMethodField()
    growth_objectives = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationRole
        fields = ['id', 'name', 'description', 'technical_objectives', 'collaboration_objectives', 'growth_objectives']
    
    def get_technical_objectives(self, obj):
        objectives = obj.objective_set.filter(
            category__name='TECHNICAL', 
            is_active=True
        ).order_by('title')
        return ObjectiveSerializer(objectives, many=True).data
    
    def get_collaboration_objectives(self, obj):
        objectives = obj.objective_set.filter(
            category__name='COLLABORATION', 
            is_active=True
        ).order_by('title')
        return ObjectiveSerializer(objectives, many=True).data
    
    def get_growth_objectives(self, obj):
        objectives = obj.objective_set.filter(
            category__name='GROWTH', 
            is_active=True
        ).order_by('title')
        return ObjectiveSerializer(objectives, many=True).data


class QuarterSerializer(serializers.ModelSerializer):
    quarter_display = serializers.CharField(source='get_quarter_display', read_only=True)
    evaluations_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quarter
        fields = ['id', 'year', 'quarter', 'quarter_display', 'start_date', 'end_date', 'is_active', 'evaluations_count']
        
    def get_evaluations_count(self, obj):
        return obj.employeeevaluation_set.count()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email']


class EvaluationAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationAttachment
        fields = [
            'id', 'file', 'file_url', 'filename', 'file_size', 
            'uploaded_by', 'uploaded_by_name', 'uploaded_at'
        ]
        read_only_fields = ['uploaded_by', 'uploaded_at', 'file_size']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class EvaluationObjectiveSerializer(serializers.ModelSerializer):
    objective_title = serializers.CharField(source='objective.title', read_only=True)
    objective_category = serializers.CharField(source='objective.category.display_name', read_only=True)
    objective_category_code = serializers.CharField(source='objective.category.name', read_only=True)
    effective_description = serializers.CharField(source='get_effective_description', read_only=True)
    effective_weight = serializers.DecimalField(source='get_effective_weight', max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = EvaluationObjective
        fields = [
            'id', 'objective', 'objective_title', 'objective_category', 'objective_category_code',
            'custom_description', 'custom_weight', 'effective_description', 'effective_weight',
            'score', 'evaluator_comments', 'employee_comments', 'evaluated_at'
        ]


class EmployeeEvaluationSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_email = serializers.CharField(source='employee.email', read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.get_full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    quarter_display = serializers.CharField(source='quarter.__str__', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    objectives = EvaluationObjectiveSerializer(many=True, read_only=True)
    attachments = EvaluationAttachmentSerializer(many=True, read_only=True)
    
    # Estadísticas calculadas
    objectives_count = serializers.SerializerMethodField()
    evaluated_objectives_count = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeeEvaluation
        fields = [
            'id', 'employee', 'employee_name', 'employee_email',
            'quarter', 'quarter_display', 'role', 'role_name',
            'supervisor', 'supervisor_name', 'status', 'status_display',
            'assigned_date', 'objectives_sent_date', 'evaluation_completed_date',
            'assignment_notes', 'evaluation_notes', 'overall_score',
            'objectives', 'attachments', 'objectives_count', 
            'evaluated_objectives_count', 'completion_percentage'
        ]
        read_only_fields = ['assigned_date', 'overall_score']
    
    def get_objectives_count(self, obj):
        return obj.objectives.count()
    
    def get_evaluated_objectives_count(self, obj):
        return obj.objectives.filter(score__isnull=False).count()
    
    def get_completion_percentage(self, obj):
        total = obj.objectives.count()
        if total == 0:
            return 0
        evaluated = obj.objectives.filter(score__isnull=False).count()
        return round((evaluated / total) * 100, 1)


class EmployeeEvaluationCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear evaluaciones"""
    objective_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="IDs de objetivos a asignar. Si no se especifica, se asignan todos los objetivos activos del rol."
    )
    
    class Meta:
        model = EmployeeEvaluation
        fields = [
            'employee', 'quarter', 'role', 'supervisor', 
            'assignment_notes', 'objective_ids'
        ]
    
    def create(self, validated_data):
        objective_ids = validated_data.pop('objective_ids', None)
        evaluation = super().create(validated_data)
        
        # Asignar objetivos
        if objective_ids:
            objectives = Objective.objects.filter(id__in=objective_ids, role=evaluation.role, is_active=True)
        else:
            objectives = Objective.objects.filter(role=evaluation.role, is_active=True)
        
        for objective in objectives:
            EvaluationObjective.objects.create(
                evaluation=evaluation,
                objective=objective
            )
        
        return evaluation


class EvaluationSummarySerializer(serializers.Serializer):
    """Serializer para resúmenes de evaluación por trimestre/departamento"""
    quarter = QuarterSerializer(read_only=True)
    total_evaluations = serializers.IntegerField()
    assigned_evaluations = serializers.IntegerField()
    in_progress_evaluations = serializers.IntegerField()
    completed_evaluations = serializers.IntegerField()
    average_score = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    
    # Por categoría
    technical_avg = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    collaboration_avg = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    growth_avg = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
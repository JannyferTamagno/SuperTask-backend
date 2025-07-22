# tasks/serializers.py
from rest_framework import serializers
from .models import Task, Category

class CategorySerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'task_count', 'created_at', 'updated_at']

    def get_task_count(self, obj):
        return obj.task_set.count()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TaskSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status', 
            'due_date', 'category', 'category_name', 'is_overdue',
            'created_at', 'updated_at', 'completed_at'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_category(self, value):
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("You can only assign tasks to your own categories.")
        return value

class TaskCreateUpdateSerializer(TaskSerializer):
    """Serializer específico para criação e atualização de tasks"""
    pass

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas do dashboard"""
    completed = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    overdue = serializers.IntegerField()
    high_priority = serializers.IntegerField()
    due_today = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    categories_stats = serializers.DictField()
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

class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer específico para criação e atualização de tasks"""
    category_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    category = serializers.PrimaryKeyRelatedField(read_only=True) 
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status', 
            'due_date', 'category', 'category_name', 'is_overdue',
            'created_at', 'updated_at', 'completed_at'
        ]

    def validate_category_name(self, value):
        """Valida e processa o nome da categoria"""
        if not value:
            return value
        
        category_name_lower = value.lower().strip()
        
        user = self.context['request'].user
        try:
            category = Category.objects.get(
                name__iexact=category_name_lower, 
                user=user
            )
            return category_name_lower
        except Category.DoesNotExist:
            raise serializers.ValidationError(f"Categoria '{value}' não encontrada.")
        except Category.MultipleObjectsReturned:
            category = Category.objects.filter(
                name__iexact=category_name_lower,
                user=user
            ).first()
            return category_name_lower

    def create(self, validated_data):
        category_name = validated_data.pop('category_name', None)
        user = self.context['request'].user  # ✅ Definir user antes do if
        
        if category_name:
            category = Category.objects.get(
                name__iexact=category_name,
                user=user
            )
            validated_data['category'] = category
        
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        category_name = validated_data.pop('category_name', None)
        
        if category_name is not None:  
            if category_name:   
                user = self.context['request'].user
                category = Category.objects.get(
                    name__iexact=category_name,
                    user=user
                )
                validated_data['category'] = category
            else:
                validated_data['category'] = None
        
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Customiza a representação de saída"""
        data = super().to_representation(instance)
        if instance.category:
            data['category_name'] = instance.category.name
        else:
            data['category_name'] = None
        return data

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas do dashboard"""
    completed = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    overdue = serializers.IntegerField()
    high_priority = serializers.IntegerField()
    due_today = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    categories_stats = serializers.DictField()
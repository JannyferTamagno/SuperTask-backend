# tasks/views.py
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count, Case, When, IntegerField
from django.utils import timezone
from datetime import date
import requests

from .models import Task, Category
from .serializers import (
    TaskSerializer, 
    CategorySerializer, 
    DashboardStatsSerializer,
    TaskCreateUpdateSerializer
)

class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class TaskListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateUpdateSerializer
        return TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)
        
        # Filtros
        priority = self.request.query_params.get('priority')
        status_filter = self.request.query_params.get('status')
        category = self.request.query_params.get('category')
        due_date = self.request.query_params.get('due_date')
        
        if priority:
            queryset = queryset.filter(priority=priority)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if category:
            queryset = queryset.filter(category=category)
            
        if due_date:
            if due_date == 'today':
                queryset = queryset.filter(due_date=date.today())
            elif due_date == 'overdue':
                queryset = queryset.filter(due_date__lt=date.today(), status__ne='completed')
        
        # Ordenação
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering == 'due_date':
            queryset = queryset.order_by('due_date', '-created_at')
        elif ordering == 'priority':
            # Ordenar por prioridade: high, medium, low
            queryset = queryset.order_by(
                Case(
                    When(priority='high', then=1),
                    When(priority='medium', then=2),
                    When(priority='low', then=3),
                    default=4,
                    output_field=IntegerField(),
                )
            )
        else:
            queryset = queryset.order_by(ordering)
        
        return queryset

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskCreateUpdateSerializer
        return TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """Endpoint para estatísticas do dashboard"""
    user = request.user
    tasks = Task.objects.filter(user=user)
    
    # Estatísticas básicas
    completed = tasks.filter(status='completed').count()
    in_progress = tasks.filter(status='in_progress').count()
    overdue = tasks.filter(due_date__lt=date.today(), status__ne='completed').count()
    high_priority = tasks.filter(priority='high', status__ne='completed').count()
    due_today = tasks.filter(due_date=date.today(), status__ne='completed').count()
    total_tasks = tasks.count()
    
    # Estatísticas por categoria
    categories_stats = {}
    for category in Category.objects.filter(user=user):
        categories_stats[category.name] = {
            'total': tasks.filter(category=category).count(),
            'completed': tasks.filter(category=category, status='completed').count(),
            'pending': tasks.filter(category=category, status__ne='completed').count(),
        }
    
    data = {
        'completed': completed,
        'in_progress': in_progress,
        'overdue': overdue,
        'high_priority': high_priority,
        'due_today': due_today,
        'total_tasks': total_tasks,
        'categories_stats': categories_stats
    }
    
    serializer = DashboardStatsSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def daily_quote(request):
    """Endpoint para buscar citação diária da API externa"""
    try:
        response = requests.get('https://api.quotable.io/random')
        if response.status_code == 200:
            quote_data = response.json()
            return Response({
                'quote': quote_data.get('content'),
                'author': quote_data.get('author')
            })
        else:
            return Response({
                'quote': 'Success is not final, failure is not fatal: It is the courage to continue that counts.',
                'author': 'Winston Churchill'
            })
    except Exception as e:
        # Fallback quote em caso de erro
        return Response({
            'quote': 'The only way to do great work is to love what you do.',
            'author': 'Steve Jobs'
        })

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def toggle_task_status(request, pk):
    """Endpoint para alternar status da tarefa entre completed/pending"""
    try:
        task = Task.objects.get(pk=pk, user=request.user)
        
        if task.status == 'completed':
            task.status = 'pending'
        else:
            task.status = 'completed'
            
        task.save()
        serializer = TaskSerializer(task)
        return Response(serializer.data)
        
    except Task.DoesNotExist:
        return Response(
            {'error': 'Task not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
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
    
    try:
        tasks = Task.objects.filter(user=user)
        today = date.today()
        
        # Estatísticas básicas - com debug
        completed = tasks.filter(status='completed').count()
        in_progress = tasks.filter(status='in_progress').count()
        overdue = tasks.filter(due_date__lt=today).exclude(status='completed').count()
        high_priority = tasks.filter(priority='high').exclude(status='completed').count()
        
        # Corrigir due_today - usar apenas pending e in_progress
        due_today = tasks.filter(
            due_date=today,  # ✅ Corrigido: today em vez de date.today
            status__in=['pending', 'in_progress']
        ).count()
        
        total_tasks = tasks.count()
        
        # Debug das tarefas para hoje
        due_today_tasks = tasks.filter(due_date=today)
        print(f"🔍 Debug due_today:")
        print(f"   - Total tarefas com due_date hoje: {due_today_tasks.count()}")
        print(f"   - Data de hoje: {today}")
        for task in due_today_tasks:
            print(f"   - Task: {task.title} | Status: {task.status} | Due: {task.due_date}")
        print(f"   - Due today count final: {due_today}")
        
        # Estatísticas por categoria
        categories_stats = {}
        try:
            categories = Category.objects.filter(user=user)
            for category in categories:
                category_tasks = tasks.filter(category=category)
                categories_stats[category.name] = {
                    'total': category_tasks.count(),
                    'completed': category_tasks.filter(status='completed').count(),
                    'pending': category_tasks.exclude(status='completed').count(),
                }
        except Exception as e:
            print(f"Erro ao processar categorias: {e}")
            categories_stats = {}
        
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
        
    except Exception as e:
        print(f"Erro no dashboard_stats: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': 'Erro interno do servidor',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def daily_quote(request):
    """Endpoint para buscar citação diária usando API quotable.io/quotes/random"""
    
    # Lista de citações motivacionais em inglês como backup
    fallback_quotes = [
        {
            'quote': 'The only way to do great work is to love what you do.',
            'author': 'Steve Jobs'
        },
        {
            'quote': 'Success is not final, failure is not fatal: It is the courage to continue that counts.',
            'author': 'Winston Churchill'
        },
        {
            'quote': 'The future belongs to those who believe in the beauty of their dreams.',
            'author': 'Eleanor Roosevelt'
        },
        {
            'quote': 'It is during our darkest moments that we must focus to see the light.',
            'author': 'Aristotle'
        },
        {
            'quote': 'The only impossible journey is the one you never begin.',
            'author': 'Tony Robbins'
        },
        {
            'quote': 'In the middle of difficulty lies opportunity.',
            'author': 'Albert Einstein'
        },
        {
            'quote': 'Believe you can and you\'re halfway there.',
            'author': 'Theodore Roosevelt'
        },
        {
            'quote': 'The way to get started is to quit talking and begin doing.',
            'author': 'Walt Disney'
        },
        {
            'quote': 'Don\'t let yesterday take up too much of today.',
            'author': 'Will Rogers'
        },
        {
            'quote': 'You learn more from failure than from success.',
            'author': 'Unknown'
        }
    ]
    
    try:
        # Usando o endpoint correto da API quotable
        response = requests.get('https://api.quotable.io/quotes/random', timeout=10)
        
        if response.status_code == 200:
            quote_data = response.json()
            
            # A API retorna um array, então pegamos o primeiro item
            if isinstance(quote_data, list) and len(quote_data) > 0:
                quote_item = quote_data[0]
                external_quote = {
                    'quote': quote_item.get('content'),
                    'author': quote_item.get('author'),
                    'source': 'quotable_api'
                }
                
                # Verifica se não é uma citação vazia
                if external_quote['quote'] and external_quote['author']:
                    return Response(external_quote)
            
            # Se não retornou array ou está vazio, tenta como objeto único
            elif isinstance(quote_data, dict):
                external_quote = {
                    'quote': quote_data.get('content'),
                    'author': quote_data.get('author'),
                    'source': 'quotable_api'
                }
                
                if external_quote['quote'] and external_quote['author']:
                    return Response(external_quote)
        
        # Se chegou aqui, a API externa falhou ou retornou dados inválidos
        import random
        selected_quote = random.choice(fallback_quotes)
        selected_quote['source'] = 'fallback'
        return Response(selected_quote)
        
    except requests.exceptions.Timeout:
        # Timeout da API externa - usa fallback
        import random
        selected_quote = random.choice(fallback_quotes)
        selected_quote['source'] = 'fallback_timeout'
        return Response(selected_quote)
        
    except Exception as e:
        # Qualquer outro erro - usa fallback
        import random
        selected_quote = random.choice(fallback_quotes)
        selected_quote['source'] = 'fallback_error'
        return Response(selected_quote)

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
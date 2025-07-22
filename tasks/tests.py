# tasks/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta
from unittest.mock import patch
from .models import Task, Category


class CategoryModelTest(TestCase):
    """Testes para o modelo Category"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Work',
            color='#ff6b6b',
            user=self.user
        )
    
    def test_category_creation(self):
        """Testa se a categoria foi criada corretamente"""
        self.assertEqual(self.category.name, 'Work')
        self.assertEqual(self.category.color, '#ff6b6b')
        self.assertEqual(self.category.user, self.user)
    
    def test_category_str_method(self):
        """Testa o método __str__ da Category"""
        self.assertEqual(str(self.category), 'Work')
    
    def test_category_default_color(self):
        """Testa se a cor padrão é aplicada"""
        category = Category.objects.create(
            name='Personal',
            user=self.user
        )
        self.assertEqual(category.color, '#007bff')


class TaskModelTest(TestCase):
    """Testes para o modelo Task"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Work',
            user=self.user
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='Test description',
            priority='high',
            status='pending',
            due_date=date.today() + timedelta(days=1),
            category=self.category,
            user=self.user
        )
    
    def test_task_creation(self):
        """Testa se a tarefa foi criada corretamente"""
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.priority, 'high')
        self.assertEqual(self.task.status, 'pending')
        self.assertEqual(self.task.user, self.user)
        self.assertEqual(self.task.category, self.category)
    
    def test_task_str_method(self):
        """Testa o método __str__ da Task"""
        self.assertEqual(str(self.task), 'Test Task')
    
    def test_task_default_values(self):
        """Testa os valores padrão da Task"""
        task = Task.objects.create(
            title='Simple Task',
            user=self.user
        )
        self.assertEqual(task.priority, 'medium')
        self.assertEqual(task.status, 'pending')
        self.assertIsNone(task.completed_at)
    
    def test_task_completed_at_auto_set(self):
        """Testa se completed_at é definido automaticamente"""
        self.task.status = 'completed'
        self.task.save()
        
        self.assertIsNotNone(self.task.completed_at)
    
    def test_task_completed_at_cleared_when_not_completed(self):
        """Testa se completed_at é limpo quando status não é completed"""
        self.task.status = 'completed'
        self.task.save()
        
        self.task.status = 'pending'
        self.task.save()
        
        self.assertIsNone(self.task.completed_at)
    
    def test_is_overdue_property(self):
        """Testa a propriedade is_overdue"""
        # Tarefa com data vencida
        overdue_task = Task.objects.create(
            title='Overdue Task',
            due_date=date.today() - timedelta(days=1),
            status='pending',
            user=self.user
        )
        self.assertTrue(overdue_task.is_overdue)
        
        # Tarefa futura
        future_task = Task.objects.create(
            title='Future Task',
            due_date=date.today() + timedelta(days=1),
            status='pending',
            user=self.user
        )
        self.assertFalse(future_task.is_overdue)
        
        # Tarefa completa (não deve ser overdue)
        completed_task = Task.objects.create(
            title='Completed Task',
            due_date=date.today() - timedelta(days=1),
            status='completed',
            user=self.user
        )
        self.assertFalse(completed_task.is_overdue)


class CategoryAPITest(APITestCase):
    """Testes para os endpoints de categorias"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        
        self.category_list_url = reverse('category-list-create')
        
        self.category = Category.objects.create(
            name='Work',
            color='#ff6b6b',
            user=self.user
        )
        
        self.category_detail_url = reverse('category-detail', kwargs={'pk': self.category.pk})
        
        # Autentica o usuário
        self.client.force_authenticate(user=self.user)
    
    def test_list_categories(self):
        """Testa listagem de categorias"""
        response = self.client.get(self.category_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Work')
    
    def test_create_category_success(self):
        """Testa criação de categoria com dados válidos"""
        data = {
            'name': 'Personal',
            'color': '#4CAF50'
        }
        
        response = self.client.post(self.category_list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Personal')
        self.assertEqual(response.data['color'], '#4CAF50')
        
        # Verifica se foi criada no banco
        self.assertTrue(Category.objects.filter(name='Personal', user=self.user).exists())
    
    def test_create_category_without_color(self):
        """Testa criação de categoria sem especificar cor"""
        data = {'name': 'Health'}
        
        response = self.client.post(self.category_list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['color'], '#007bff')  # Cor padrão
    
    def test_get_category_detail(self):
        """Testa obtenção de detalhes de uma categoria"""
        response = self.client.get(self.category_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Work')
    
    def test_update_category(self):
        """Testa atualização de categoria"""
        data = {
            'name': 'Work Updated',
            'color': '#4CAF50'
        }
        
        response = self.client.put(self.category_detail_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Work Updated')
        
        # Verifica se foi atualizada no banco
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Work Updated')
    
    def test_delete_category(self):
        """Testa exclusão de categoria"""
        response = self.client.delete(self.category_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verifica se foi excluída do banco
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())
    
    def test_user_can_only_see_own_categories(self):
        """Testa se usuário só vê suas próprias categorias"""
        # Cria categoria para outro usuário
        Category.objects.create(
            name='Other User Category',
            user=self.other_user
        )
        
        response = self.client.get(self.category_list_url)
        
        # Deve retornar apenas 1 categoria (do usuário atual)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Work')


class TaskAPITest(APITestCase):
    """Testes para os endpoints de tarefas"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Work',
            user=self.user
        )
        
        self.task_list_url = reverse('task-list-create')
        
        self.task = Task.objects.create(
            title='Test Task',
            description='Test description',
            priority='high',
            status='pending',
            due_date=date.today() + timedelta(days=1),
            category=self.category,
            user=self.user
        )
        
        self.task_detail_url = reverse('task-detail', kwargs={'pk': self.task.pk})
        self.toggle_status_url = reverse('toggle-task-status', kwargs={'pk': self.task.pk})
        
        # Autentica o usuário
        self.client.force_authenticate(user=self.user)
    
    def test_list_tasks(self):
        """Testa listagem de tarefas"""
        response = self.client.get(self.task_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Task')
    
    def test_create_task_success(self):
        """Testa criação de tarefa com dados válidos"""
        data = {
            'title': 'New Task',
            'description': 'New description',
            'priority': 'medium',
            'status': 'pending',
            'due_date': str(date.today() + timedelta(days=2)),
            'category': self.category.pk
        }
        
        response = self.client.post(self.task_list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Task')
        self.assertEqual(response.data['category'], self.category.pk)
        
        # Verifica se foi criada no banco
        self.assertTrue(Task.objects.filter(title='New Task', user=self.user).exists())
    
    def test_create_task_minimal_data(self):
        """Testa criação de tarefa com dados mínimos"""
        data = {'title': 'Simple Task'}
        
        response = self.client.post(self.task_list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Simple Task')
        self.assertEqual(response.data['priority'], 'medium')  # Valor padrão
        self.assertEqual(response.data['status'], 'pending')   # Valor padrão
    
    def test_get_task_detail(self):
        """Testa obtenção de detalhes de uma tarefa"""
        response = self.client.get(self.task_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Task')
        self.assertEqual(response.data['category_name'], 'Work')
    
    def test_update_task(self):
        """Testa atualização de tarefa"""
        data = {
            'title': 'Updated Task',
            'priority': 'low',
            'status': 'in_progress'
        }
        
        response = self.client.patch(self.task_detail_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Task')
        self.assertEqual(response.data['priority'], 'low')
        
        # Verifica se foi atualizada no banco
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
    
    def test_delete_task(self):
        """Testa exclusão de tarefa"""
        response = self.client.delete(self.task_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verifica se foi excluída do banco
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())
    
    def test_toggle_task_status(self):
        """Testa alternância de status da tarefa"""
        # Status inicial: pending
        self.assertEqual(self.task.status, 'pending')
        
        # Alterna para completed
        response = self.client.patch(self.toggle_status_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        
        # Alterna de volta para pending
        response = self.client.patch(self.toggle_status_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'pending')
    
    def test_filter_tasks_by_priority(self):
        """Testa filtro de tarefas por prioridade"""
        # Cria tarefa com prioridade diferente
        Task.objects.create(
            title='Low Priority Task',
            priority='low',
            user=self.user
        )
        
        response = self.client.get(self.task_list_url, {'priority': 'high'})
        
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['priority'], 'high')
    
    def test_filter_tasks_by_status(self):
        """Testa filtro de tarefas por status"""
        # Cria tarefa com status diferente
        Task.objects.create(
            title='Completed Task',
            status='completed',
            user=self.user
        )
        
        response = self.client.get(self.task_list_url, {'status': 'pending'})
        
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'pending')
    
    def test_user_can_only_see_own_tasks(self):
        """Testa se usuário só vê suas próprias tarefas"""
        # Cria tarefa para outro usuário
        Task.objects.create(
            title='Other User Task',
            user=self.other_user
        )
        
        response = self.client.get(self.task_list_url)
        
        # Deve retornar apenas 1 tarefa (do usuário atual)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Task')


class DashboardAPITest(APITestCase):
    """Testes para os endpoints do dashboard"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Work',
            user=self.user
        )
        
        # Cria tarefas com diferentes status
        Task.objects.create(
            title='Completed Task',
            status='completed',
            priority='high',
            category=self.category,
            user=self.user
        )
        
        Task.objects.create(
            title='In Progress Task',
            status='in_progress',
            priority='medium',
            user=self.user
        )
        
        Task.objects.create(
            title='Overdue Task',
            status='pending',
            due_date=date.today() - timedelta(days=1),
            priority='high',
            user=self.user
        )
        
        Task.objects.create(
            title='Due Today Task',
            status='pending',
            due_date=date.today(),
            priority='low',
            user=self.user
        )
        
        self.stats_url = reverse('dashboard-stats')
        self.quote_url = reverse('daily-quote')
        
        # Autentica o usuário
        self.client.force_authenticate(user=self.user)
    
    def test_dashboard_stats(self):
        """Testa endpoint de estatísticas do dashboard"""
        response = self.client.get(self.stats_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica as estatísticas
        self.assertEqual(response.data['completed'], 1)
        self.assertEqual(response.data['in_progress'], 1)
        self.assertEqual(response.data['overdue'], 1)
        self.assertEqual(response.data['high_priority'], 1)  # Apenas a overdue (completed não conta)
        self.assertEqual(response.data['due_today'], 1)
        self.assertEqual(response.data['total_tasks'], 4)
        
        # Verifica estatísticas por categoria
        self.assertIn('categories_stats', response.data)
        self.assertIn('Work', response.data['categories_stats'])
    
    @patch('tasks.views.requests.get')
    def test_daily_quote_success(self, mock_get):
        """Testa endpoint de citação diária com sucesso da API externa"""
        # Mock da resposta da API externa
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'content': 'Test quote',
            'author': 'Test Author'
        }
        
        response = self.client.get(self.quote_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quote'], 'Test quote')
        self.assertEqual(response.data['author'], 'Test Author')
    
    @patch('tasks.views.requests.get')
    def test_daily_quote_fallback(self, mock_get):
        """Testa endpoint de citação diária com fallback"""
        # Mock de falha na API externa
        mock_get.side_effect = Exception('API Error')
        
        response = self.client.get(self.quote_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('quote', response.data)
        self.assertIn('author', response.data)
        # Deve ser uma das frases de fallback
        fallback_authors = ['Steve Jobs', 'Winston Churchill', 'Eleanor Roosevelt']
        self.assertIn(response.data['author'], fallback_authors)
    
    def test_dashboard_endpoints_require_authentication(self):
        """Testa se os endpoints do dashboard requerem autenticação"""
        # Remove autenticação
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.get(self.quote_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
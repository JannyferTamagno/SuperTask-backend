# accounts/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile


class UserModelTest(TestCase):
    """Testes para o modelo User e UserProfile"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_creation(self):
        """Testa se o usuário foi criado corretamente"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_user_profile_created_automatically(self):
        """Testa se o perfil do usuário é criado automaticamente"""
        self.assertTrue(hasattr(self.user, 'userprofile'))
        self.assertIsInstance(self.user.userprofile, UserProfile)
    
    def test_user_profile_str_method(self):
        """Testa o método __str__ do UserProfile"""
        expected_str = f"{self.user.username}'s Profile"
        self.assertEqual(str(self.user.userprofile), expected_str)


class AuthenticationAPITest(APITestCase):
    """Testes para os endpoints de autenticação"""
    
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('profile')
        self.user_info_url = reverse('user_info')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_user_registration_success(self):
        """Testa registro de usuário com dados válidos"""
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['message'], 'User created successfully')
        
        # Verifica se o usuário foi criado no banco
        self.assertTrue(User.objects.filter(username='testuser').exists())
    
    def test_user_registration_password_mismatch(self):
        """Testa registro com senhas que não coincidem"""
        data = self.user_data.copy()
        data['password_confirm'] = 'different_password'
        
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
    
    def test_user_registration_missing_fields(self):
        """Testa registro com campos obrigatórios faltando"""
        data = {'username': 'testuser'}
        
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login_success(self):
        """Testa login com credenciais válidas"""
        # Primeiro, cria um usuário
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['message'], 'Login successful')
    
    def test_user_login_invalid_credentials(self):
        """Testa login com credenciais inválidas"""
        login_data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_user_login_missing_fields(self):
        """Testa login com campos faltando"""
        login_data = {'username': 'testuser'}
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_user_info_authenticated(self):
        """Testa obtenção de informações do usuário autenticado"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Autentica o usuário
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.user_info_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_get_user_info_unauthenticated(self):
        """Testa obtenção de informações sem autenticação"""
        response = self.client.get(self.user_info_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile(self):
        """Testa atualização do perfil do usuário"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client.force_authenticate(user=user)
        
        # Use PATCH em vez de PUT para atualização parcial
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        
        response = self.client.patch(self.profile_url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se os dados foram atualizados
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.last_name, 'Name')
        self.assertEqual(user.email, 'updated@example.com')


class ChangePasswordTest(APITestCase):
    """Testes para mudança de senha"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='oldpass123'
        )
        self.change_password_url = reverse('change_password')
        self.client.force_authenticate(user=self.user)
    
    def test_change_password_success(self):
        """Testa mudança de senha com dados válidos"""
        data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = self.client.post(self.change_password_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password changed successfully')
        
        # Verifica se a senha foi realmente alterada
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))
        self.assertFalse(self.user.check_password('oldpass123'))
    
    def test_change_password_wrong_old_password(self):
        """Testa mudança de senha com senha atual incorreta"""
        data = {
            'old_password': 'wrongpass',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = self.client.post(self.change_password_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_change_password_mismatch(self):
        """Testa mudança de senha com confirmação incorreta"""
        data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'differentpass'
        }
        
        response = self.client.post(self.change_password_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
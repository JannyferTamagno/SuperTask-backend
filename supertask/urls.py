from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def home_view(request):
    """View simples para a página inicial"""
    try:
        logger.info(f"Home view accessed: {request.method} {request.path}")
        
        response_data = {
            'message': '🎉 Bem-vindo à SuperTask API!',
            'version': '1.0.0',
            'status': 'online',
            'method': request.method,
            'path': request.path,
            'host': request.get_host(),
            'endpoints': {
                'admin': '/admin/',
                'auth': {
                    'register': '/api/auth/register/',
                    'login': '/api/auth/login/',
                    'logout': '/api/auth/logout/',
                    'profile': '/api/auth/profile/',
                    'user_info': '/api/auth/user/',
                },
                'tasks': {
                    'list_create': '/api/tasks/',
                    'detail': '/api/tasks/{id}/',
                    'toggle_status': '/api/tasks/{id}/toggle-status/',
                },
                'categories': {
                    'list_create': '/api/categories/',
                    'detail': '/api/categories/{id}/',
                },
                'dashboard': {
                    'stats': '/api/dashboard/stats/',
                    'quote': '/api/dashboard/quote/',
                }
            },
            'docs': 'Esta é uma API REST para gerenciamento de tarefas.',
            'author': 'Jannyfer Tamagno',
            'deploy_status': 'Funcionando perfeitamente! 🚀'
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Erro na home view: {str(e)}")
        return JsonResponse({
            'error': 'Erro interno',
            'message': str(e)
        }, status=500)

@csrf_exempt  
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'SuperTask API',
        'timestamp': str(request.GET.get('timestamp', 'now')),
        'method': request.method
    })

urlpatterns = [
    path('', home_view, name='home'),  # Rota da home
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('tasks.urls')),
]
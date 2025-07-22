from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def home_view(request):
    """View simples para a página inicial"""
    return JsonResponse({
        'message': 'Bem-vindo à SuperTask API!',
        'version': '1.0.0',
        'status': 'online',
        'endpoints': {
            'admin': '/admin/',
            'auth': '/api/auth/',
            'tasks': '/api/tasks/',
            'categories': '/api/categories/',
            'dashboard': '/api/dashboard/stats/',
        },
        'docs': 'Esta é uma API REST para gerenciamento de tarefas.'
    })

urlpatterns = [
    path('', home_view, name='home'),  # Rota da home
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('tasks.urls')),
]
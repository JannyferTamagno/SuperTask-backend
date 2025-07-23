from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile_and_categories(sender, instance, created, **kwargs):
    """Cria perfil do usuário e categorias padrão quando um novo usuário é criado"""
    if created:
        # Criar perfil do usuário
        UserProfile.objects.create(user=instance)
        
        # Importar Category aqui para evitar import circular
        from tasks.models import Category
        
        # Criar categorias padrão
        default_categories = [
            {"name": "Trabalho", "color": "#3b82f6"},
            {"name": "Estudos", "color": "#10b981"},
            {"name": "Lazer", "color": "#f59e0b"},
            {"name": "Pessoal", "color": "#ef4444"},
        ]
        
        for category_data in default_categories:
            Category.objects.create(
                name=category_data["name"],
                color=category_data["color"],
                user=instance
            )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Salva o perfil do usuário quando o usuário é salvo"""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
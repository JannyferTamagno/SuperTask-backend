from django.contrib import admin
from .models import Task, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'user', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'status', 'due_date', 'category', 'user', 'created_at']
    list_filter = ['priority', 'status', 'category', 'user', 'created_at', 'due_date']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
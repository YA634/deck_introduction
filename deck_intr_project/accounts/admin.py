from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser

class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'is_staff']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['email', 'username']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('個人情報', {'fields': ('username',)}),
        ('権限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)
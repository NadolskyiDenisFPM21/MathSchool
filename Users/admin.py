from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Основные поля, которые будут отображаться в списке пользователей
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    # Группировка полей при редактировании пользователя
    fieldsets = (
        (_('Основна інформація'), {'fields': ('username', 'password')}),
        (_('Особисті дані'), {'fields': ('first_name', 'last_name', 'email', 'role')}),
        (_('Права доступу'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Важливі дати'), {'fields': ('last_login', 'date_joined')}),
    )

    # Поля, доступные при создании нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2'),
        }),
    )

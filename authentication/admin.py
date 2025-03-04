from django.contrib import admin
from .models import AppUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(AppUser)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', "first_name", "last_name", "is_staff", "public_id"]
    search_fields = ['email', "first_name", "last_name", "phone_number"]
    ordering = ['email']
    fieldsets = (
        (
            None, {"fields": ("password",)}
        ),
        (
            "Informacje osobiste", {"fields": ('first_name', 'last_name', 'email', "phone_number")}
        ),
        (
            "Uprawnienia", {"fields": ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}
        ),
        (
            "Ważne daty", {"fields": ("last_login",)}
        )
    )

    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': ("first_name", "last_name", 'email', 'phone_number', 'password1', 'password2'),
            }
        ),
    )

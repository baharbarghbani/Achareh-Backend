from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role  
from django.contrib.auth.admin import UserAdmin


@admin.register(Role)
class CustomRoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id','name']
    search_fields = ['id','name']


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    readonly_fields = ("last_login", "date_joined")

    fieldsets = (
        ("Account", {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "phone_number")}),
        ("Roles", {"fields": ("roles",)}),
        ("Status", {"fields": ("is_active",)}),
    )

    filter_horizontal = ("roles",)


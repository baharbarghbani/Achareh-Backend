from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role


admin.site.register(Role)
admin.site.register(User)
# class RoleAdmin(admin.ModelAdmin):
#     list_display = ['id', 'name']
#     list_display_links = ['name']
#     search_fields = ['name']


# class UserAdmin(BaseUserAdmin):
#     fieldsets = BaseUserAdmin.fieldsets + (
#         ('نقش‌ها', {'fields': ('roles',)}),
#     )
#     add_fieldsets = BaseUserAdmin.add_fieldsets + (
#         ('نقش‌ها', {'fields': ('roles',)}),
#     )
#     filter_horizontal = ['roles'] 
#     list_display = ['username', 'email', 'get_roles', 'is_staff', 'date_joined']
#     list_filter = ['roles', 'is_staff', 'is_superuser', 'is_active']
    
#     def get_roles(self, obj):
#         return ", ".join([role.name for role in obj.roles.all()])
#     get_roles.short_description = 'نقش‌ها'

from django.contrib import admin
from .models import Request

# Register your models here.
@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'performer', 'status', 'created_at', 'ad')
    list_filter = ('status', 'created_at', 'ad__category')
    search_fields = ('ad__title', 'ad__description', 'performer__username')
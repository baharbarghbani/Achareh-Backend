from django.contrib import admin

# Register your models here.
from .models import Ad
@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'performer', 'status', 'date_added')
    list_filter = ('status', 'date_added', 'category')
    search_fields = ('title', 'description', 'creator__username', 'performer__username')
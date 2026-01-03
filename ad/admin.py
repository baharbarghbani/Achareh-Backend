from django.contrib import admin

# Register your models here.
from .models import Ad, AdRequest


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "creator", "performer", "status", "date_added")
    list_filter = ("status", "date_added", "category")
    search_fields = ("title", "description", "creator__username", "performer__username")

    readonly_fields = ("performer",)  # cannot edit performer in admin



@admin.register(AdRequest)
class AdRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'ad', 'performer', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('ad__title', 'performer__username')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "performer":
            kwargs["queryset"] = db_field.related_model.objects.filter(
                roles__name="performer"
            ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

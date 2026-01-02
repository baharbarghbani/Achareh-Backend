from django.contrib import admin
from .models import Comment

admin.site.register(Comment)

# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     """
#     مدیریت نظرات در پنل ادمین
#     """
#     list_display = ['id', 'user', 'ad', 'performer', 'rating', 'created_at']
#     list_display_links = ['id', 'user']
#     list_filter = ['rating', 'created_at', 'ad']
#     search_fields = ['content', 'user__username', 'ad__title', 'performer__username']
#     readonly_fields = ['created_at']
#     date_hierarchy = 'created_at'
    
#     fieldsets = (
#         ('اطلاعات نظر', {
#             'fields': ('content', 'rating')
#         }),
#         ('ارتباطات', {
#             'fields': ('user', 'ad', 'performer')
#         }),
#         ('تاریخ', {
#             'fields': ('created_at',)
#         }),
#     )

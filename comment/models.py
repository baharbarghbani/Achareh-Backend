from django.db import models
from ad.models import Ad
from user.models import User

class Comment(models.Model):
    class Rating(models.IntegerChoices):
        ONE = 1, '1'
        TWO = 2, '2'
        THREE = 3, '3'
        FOUR = 4, '4'
        FIVE = 5, '5'
    
    content = models.TextField()
    rating = models.IntegerField(choices=Rating.choices, verbose_name='امتیاز')
    ad = models.ForeignKey(
        Ad, 
        on_delete=models.CASCADE, 
        related_name='comments', 
        verbose_name='آگهی'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='comments', 
        verbose_name='کاربر'
    )
    performer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='performer_comments',
        verbose_name='انجام‌دهنده'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'
    
    def __str__(self):
        return f'نظر {self.user.username} برای {self.ad.title} - امتیاز: {self.rating}'
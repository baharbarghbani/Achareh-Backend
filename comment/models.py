from django.db import models
from django.conf import settings


class Comment(models.Model):
    class Rating(models.IntegerChoices):
        ONE = 1, '1'
        TWO = 2, '2'
        THREE = 3, '3'
        FOUR = 4, '4'
        FIVE = 5, '5'

    content = models.TextField(verbose_name='متن نظر')
    rating = models.IntegerField(choices=Rating.choices, verbose_name='امتیاز')

    ad = models.ForeignKey(
        'ad.Ad',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='آگهی'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments_written',
        verbose_name='کاربر'
    )

    performer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments_received',
        verbose_name='انجام‌دهنده'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'

    def __str__(self):
        return f'نظر {self.user} برای {self.ad} - امتیاز: {self.rating}'

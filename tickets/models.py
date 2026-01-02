from tabnanny import verbose
from django.db import models
from user.models import User
from ad.models import Ads


class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'باز'
        PENDING = 'pending', 'درحال بررسی'
        CLOSED = 'closed', 'بسته'
    
    title = models.CharField(max_length=255, verbose_name='عنوان')
    message = models.TextField(verbose_name='پیام')
    response = models.TextField(blank=True, null=True, verbose_name='پاسخ')
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.OPEN,
        verbose_name='وضعیت'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tickets',
        verbose_name='کاربر'
    )
    ad = models.ForeignKey(
        Ads, 
        on_delete=models.CASCADE,
        related_name='tickets',
        blank=True,
        null=True,
        verbose_name='آگهی'
    )
    
    class Meta:
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت‌ها'


    def __str__(self):
        return f'تیکت {self.id}: {self.title} - {self.get_status_display()}'

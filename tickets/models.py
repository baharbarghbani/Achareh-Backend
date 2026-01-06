from django.db import models
from django.conf import settings


class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'باز'
        PENDING = 'pending', 'درحال بررسی'
        CLOSED = 'closed', 'بسته'

    title = models.CharField(max_length=255, verbose_name='عنوان')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name='وضعیت'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='کاربر'
    )

    ad = models.ForeignKey(
        'ad.Ad',
        on_delete=models.SET_NULL,
        related_name='tickets',
        blank=True,
        null=True,
        verbose_name='آگهی',
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'تیکت {self.id}: {self.title} - {self.get_status_display()}'


class TicketMessage(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='تیکت'
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ticket_messages',
        verbose_name='ارسال‌کننده'
    )

    body = models.TextField(verbose_name='متن پیام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')

    class Meta:
        verbose_name = 'پیام تیکت'
        verbose_name_plural = 'پیام‌های تیکت'
        ordering = ['created_at']

    def __str__(self):
        return f'پیام {self.id} برای تیکت {self.ticket_id}'

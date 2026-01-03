from django.db import models
from django.conf import settings


class Ad(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'باز'
        ASSIGNED = 'assigned', 'تخصیص شده'
        DONE_REPORTED = 'done_reported', 'اعلام پایان کار'
        DONE = 'done', 'انجام شده'
        CANCELLED = 'cancelled', 'لغو شده'

    title = models.CharField(max_length=255, verbose_name='عنوان')
    description = models.TextField(verbose_name='توضیحات')
    category = models.CharField(max_length=255, verbose_name='دسته‌بندی')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name='وضعیت'
    )
    date_added = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ads_created',
        verbose_name='ایجادکننده'
    )

    performer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='ads_performed',
        null=True,
        blank=True,
        verbose_name='انجام‌دهنده'
    )

    execution_time = models.DateTimeField(null=True, blank=True, verbose_name='زمان اجرا')
    execution_location = models.CharField(max_length=500, null=True, blank=True, verbose_name='محل اجرا')

    class Meta:
        ordering = ['-date_added']
        verbose_name = 'آگهی'
        verbose_name_plural = 'آگهی‌ها'

    def __str__(self):
        return f'{self.title} - {self.get_status_display()}'


class AdRequest(models.Model):
    class Status(models.TextChoices):
           PENDING = 'pending', 'در انتظار'
           APPROVED = 'approved', 'تایید شده'
           REJECTED = 'rejected', 'رد شده'

    performer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requests_made', verbose_name='پیمانکار')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name='وضعیت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='requests', verbose_name='آگهی')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["ad", "performer"], name="unique_request_per_ad_performer")
        ]
        ordering = ['-created_at']
        verbose_name = 'درخواست'
        verbose_name_plural = 'درخواست‌ها'
    def __str__(self):
           return f'درخواست {self.id} برای آگهی {self.ad.title} توسط {self.performer.username} - {self.get_status_display()}' 
from django.db import models
from django.conf import settings
from ad import Ad

# Create your models here.
class Request(models.Model):
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

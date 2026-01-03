from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    class Names(models.TextChoices):
        CUSTOMER = "customer", "مشتری"
        PERFORMER = "performer", "پیمانکار"
        SUPPORT = "support", "پشتیبانی"
        ADMIN = "admin", "مدیر"

    name = models.CharField(max_length=50, unique=True, choices=Names.choices)

    class Meta:
        ordering = ['name']
        verbose_name = 'نقش'
        verbose_name_plural = 'نقش‌ها'

    def __str__(self):
        return self.name


class User(AbstractUser):
    roles = models.ManyToManyField(
        Role,
        blank=True,
        related_name='users',
        verbose_name='نقش‌ها',
    )
    phone_number = models.CharField(max_length=20, null=False)

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField('user.User', on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return self.user.username

from django.db import models
from django.contrib.auth.models import AbstractUser
from comment.models import Comment


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
        return f"{self.username}"


class Profile(models.Model):
    user = models.OneToOneField('user.User', on_delete=models.CASCADE, related_name='profile')
    average_rating = models.FloatField(default=0.0, verbose_name='میانگین امتیاز')
    ads = models.ManyToManyField('ad.Ad', blank=True, related_name='profiles', verbose_name='آگهی‌ها')
    comments = models.ManyToManyField(Comment, blank=True, related_name='profiles', verbose_name='نظرات')

    def __str__(self):
        return self.user.username

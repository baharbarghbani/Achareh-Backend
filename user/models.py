from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    CUSTOMER = 'customer'
    PERFORMER = 'performer'
    SUPPORT = 'support'
    ADMIN = 'admin'

    name = models.CharField(max_length=255, unique=True, verbose_name='نام نقش')
    
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
    
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
    
    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


    def __str__(self):
        return self.user.username
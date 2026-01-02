from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile, Role


@receiver(post_save, sender=User)
def build_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=User)
def create_role(sender, instance, created, **kwargs):
    if created:
        Role.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_role(sender, instance, **kwargs):
    instance.role.save()


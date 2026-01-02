from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Profile, Role

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile_and_default_role(sender, instance, created, **kwargs):
    if not created:
        return

    Profile.objects.create(user=instance)

    role, _ = Role.objects.get_or_create(name=Role.Names.CUSTOMER)
    instance.roles.add(role)

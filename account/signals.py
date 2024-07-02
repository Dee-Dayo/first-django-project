from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import User
from .models import Account


@receiver(signal=post_save, sender =User)
def create_account(created, instance, **kwargs):
    if created:
        Account.objects.create(
            user=instance,
            account_number=instance.phone[1:]
        )
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Refferal, User, UserAccount
from wallets.models import Wallet
import secrets

@receiver(post_save, sender=User)
def create_user_account(sender: User, instance: User, created: bool, **kwargs) -> None:
    if created:
        UserAccount.objects.create(owner=instance)


@receiver(post_save, sender=User)
def create_user_wallet(sender: User, instance: User, created: bool, **kwargs) -> None:
    if created:
        Wallet.objects.create(owner=instance)

@receiver(post_save, sender=User)
def create_user_refferal_code(sender: User, instance: User, created: bool, **kwargs) -> None:
    if created:
        Refferal.objects.create(owner=instance, code=secrets.token_urlsafe(50))
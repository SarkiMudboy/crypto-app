import uuid
from django.db import models
from accounts.models import TimeStampMixin, User
from django.utils.translation import gettext_lazy as _

class Wallet(TimeStampMixin, models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.OneToOneField(User, related_name="wallet", on_delete=models.CASCADE)
    coins = models.ManyToManyField('Coin', null=True, blank=True)
    total_value = models.FloatField(default=0.00)

    def __str__(self) -> str:
        return self.owner.email + " wallet"
    
    def dict(self):
        return self.__dict__

class Coin(TimeStampMixin, models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, related_name="coin", on_delete=models.CASCADE)
    cryptocurrency = models.OneToOneField('Cryptocurrency', related_name="coin", on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)

    def __str__(self) -> str:
        return f'{self.cryptocurrency.name} - ({self.amount})'
    
    def dict(self):
        return self.__dict__

class Cryptocurrency(TimeStampMixin, models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(_("Currency Symbol"), max_length=200, null=True, blank=True)
    current_price = models.FloatField(default=0.00)
    percent_change_24h = models.FloatField(default=0.00)
    high_ranking = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "cryptocurrencies"

    def __str__(self) -> str:
        return self.name
    
    def dict(self):
        return self.__dict__
    
    @property
    def price(self):
        return str(self.current_price)

from django.db.models.fields import related
from django.utils import timezone
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
from .managers import UserManager

User = settings.AUTH_USER_MODEL

class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

class User(AbstractBaseUser, PermissionsMixin, TimeStampMixin):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email_address"), unique=True)

    first_name = models.CharField(verbose_name="first name", max_length=250)
    last_name = models.CharField(verbose_name="last name", max_length=250)
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # password reset
    password_reset_key = models.CharField(max_length=100, unique=True, null=True, blank=True)
    password_reset_key_expires =  models.DateTimeField(_("Email key expires at"), null=True)
    active_password_reset_link = models.BooleanField(default=False)

    reffered_by = models.ForeignKey('User', related_name="reffered", null=True, blank=True, on_delete=models.CASCADE)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self) -> str:
        return self.email
    
    def has_perm(self, perm, obj=None) -> bool:
        return True
    
    def has_module_perms(self, app_label: str) -> bool:
        return super().has_module_perms(app_label)
    
    def dict(self):
        return self.__dict__
    
    def __str__(self) -> str:
        return self.email

class UserAccount(TimeStampMixin, models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.OneToOneField(User, related_name="account", on_delete=models.CASCADE)
    balance = models.FloatField(_("Balance ($)"), default=0.00)

    def __str__(self) -> str:
        return self.owner.email +  " account"
    

class Refferal(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.OneToOneField(User, related_name="refferal", on_delete=models.CASCADE)
    code = models.CharField(max_length=300, unique=True)

    def __str__(self) -> str:
        return f"{self.owner.email} - {self.code}"
    

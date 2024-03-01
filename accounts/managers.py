from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings

User = settings.AUTH_USER_MODEL


class UserManager(BaseUserManager):

    def create_user(self, first_name: str, last_name: str, password: str, **extra_fields) -> AbstractBaseUser:

        email = extra_fields.get("email", None)

        if not email:
            raise ValueError(_("Email must be set"))
        
        if not first_name or not last_name:
            raise ValueError(_("First name and last name must be set"))
        
        if email:
            email = self.normalize_email(email)
            extra_fields["email"] = email

        user: AbstractBaseUser = self.model(first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save()

        return user
    
    def create_superuser(self, first_name: str, last_name: str, password: str, **extra_fields) -> AbstractBaseUser:

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff set to True"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser set to True"))
        
        return self.create_user(first_name, last_name, password, **extra_fields)
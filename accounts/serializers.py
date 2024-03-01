from typing_extensions import Required
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import AbstractBaseUser
from .models import Refferal, User
from typing import Dict, Any, Tuple, List


class UserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        required=True,
        validators = [UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    refferal_code = serializers.CharField(max_length=80, required=False, allow_blank=True)

    class Meta:
        model: AbstractBaseUser = User
        fields: List[str] = ["email", "first_name", "last_name", "password", "confirm_password", "refferal_code"]
        extra_kwargs: Dict[str, dict] = {"password": {"write_only": True}, "confirm_password": {"write_only": True}}

        def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:

            if attrs.get('confirm_password'):
                if attrs['password'] != attrs['confirm_password']:
                    raise serializers.ValidationError({'password': 'Passwords must match.'})
                else:
                    raise serializers.ValidationError("Confirm password")
                
            if not attrs.get("email"):
                raise serializers.ValidationError("Email must be provided")
                
            if not attrs.get("first_name") or not attrs.get("last_name"):
                raise serializers.ValidationError("First name and Last name must be provided.")
            
            if attrs.get("refferal_code"):
                ref = Refferal.objects.filter(code=attrs.get("refferal_code"))
                if not ref.exists():
                    raise serializers.ValidationError("Invalid refferal code")
            
            return attrs
        
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
    )
    password = serializers.CharField(required=True, write_only=True)


class PasswordRecoverySerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:

        email = attrs.get("email")

        if not email:
            raise serializers.ValidationError("Please provide an email")
        elif email:
            if not User.objects.filter(email=email).exists():
                raise serializers.ValidationError("Account with that email does not exist")
           
        return attrs
    

class ResetPasswordSerializer(serializers.Serializer):

    password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs: Dict[str, Any]):

        if not attrs.get("password"):
            raise serializers.ValidationError("Please provide a password")
        
        if not attrs.get("confirm_password"):
            raise serializers.ValidationError("Confirm password")
        
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError("Passwords must match")
        
        return attrs
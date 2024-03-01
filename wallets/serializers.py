from typing_extensions import Required
from django.contrib.auth.models import AbstractBaseUser
from rest_framework import serializers
from typing import Dict, Tuple, List, Any
from accounts.models import User
from .models import Cryptocurrency


class CoinSerializer(serializers.ModelSerializer):

    cryptocurrency = serializers.PrimaryKeyRelatedField(queryset=Cryptocurrency.objects.all(), required=True)

    class Meta:
        model: AbstractBaseUser = User
        fields: List[str] = ["id", "owner", "cryptocurrency", "amount"]


class WalletSerializer(serializers.ModelSerializer):

    owner = serializers.PrimaryKeyRelatedField(queryset=Cryptocurrency.objects.all(), required=True)
    # total_value = serializers.FloatField(read_only=True, required=False)
    # coins = CoinSerializer(many=True, read_only=True, required=False)
    
    class Meta:
        model: AbstractBaseUser = User
        fields: List[str] = ["id", "owner", "coins", "total_value"]
        extra_kwargs: Dict[str, dict] = {"total_value": {"read_only": True}}

    



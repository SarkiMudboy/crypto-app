from django.contrib import admin
from .models import Cryptocurrency, Wallet


# Register your models here.
admin.site.register(Cryptocurrency)
admin.site.register(Wallet)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UserCreationForm, UserChangeForm
from .models import Refferal, User, UserAccount

class AppUserAdmin(UserAdmin):

    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    list_display = ("email", "is_staff", "is_active")
    list_filter = ("email", "is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                ("first_name", "last_name"), "email",
                "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions",
            )
        }),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(User, AppUserAdmin)

admin.site.register(UserAccount)
admin.site.register(Refferal)



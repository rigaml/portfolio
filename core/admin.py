from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Override base class `add_fieldsets` defining what fields to be displayed in admin interface
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2", "email", "first_name", "last_name"),
            },
        ),
    ) 
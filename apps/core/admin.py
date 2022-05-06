from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group

from .models import User

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ["email", "date_joined", "is_staff"]
    ordering = ["-id"]
    fieldsets = [
        (None, {"fields": ("email", "data")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        (
            "Advanced",
            {
                "classes": ("collapse",),
                "fields": ["password", "is_active", "is_staff", "is_superuser"],
            },
        ),
    ]

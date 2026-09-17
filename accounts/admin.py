from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class HospitalUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Hospital profile", {"fields": ("role", "phone", "updated_at")}),)
    readonly_fields = ("updated_at",)
    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")

from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "module", "record_id", "ip_address")
    list_filter = ("module", "action")
    search_fields = ("record_id", "user__username", "user__email")
    readonly_fields = ("created_at",)

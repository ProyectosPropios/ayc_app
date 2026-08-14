from django.contrib import admin

from .models import WorkOrder


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "title",
        "customer",
        "technician",
        "scheduled_date",
        "status",
        "priority",
    )
    list_filter = ("status", "priority", "scheduled_date")
    search_fields = ("code", "title", "customer__name", "technician__email")
    readonly_fields = ("code", "created_by", "created_at", "updated_at")

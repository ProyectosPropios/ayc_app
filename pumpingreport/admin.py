from django.contrib import admin

from .models import PumpingReport


@admin.register(PumpingReport)
class PumpingReportAdmin(admin.ModelAdmin):
    list_display = ("work_order", "report_date", "technician_name", "status", "created_at")
    list_filter = ("status", "report_date")
    search_fields = ("work_order__code", "work_order__customer__name", "technician_name")
    readonly_fields = ("created_by", "created_at", "updated_at")

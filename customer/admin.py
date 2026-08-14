from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "city", "is_active", "created_at")
    list_filter = ("is_active", "city")
    search_fields = ("name", "identification", "email", "phone", "city")
    readonly_fields = ("created_by", "created_at", "updated_at")

# core/admin.py

from django.contrib import admin
from .models import Employee
from datetime import timedelta
import uuid
from django.utils import timezone
from django.utils.html import format_html

# Register your models here.

@admin.action(description="Generate new QR codes and validate them for 30 days")
def refresh_qr_codes(modeladmin, request, queryset):
    for employee in queryset:
        employee.qr_code = uuid.uuid4()
        employee.qr_expires_at = timezone.now() + timedelta(days=30)
        employee.save()
    modeladmin.message_user(request, f"Successfuly refreshed QR codes for {queryset.count()} employees.")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'photo_preview', 
        'first_name', 
        'last_name', 
        'qr_code_status',
        'qr_image_preview',
        'qr_expires_at', 
        'is_active'
    )
    
    actions = [refresh_qr_codes]
    readonly_fields = ('qr_code', 'photo_preview', 'qr_image_preview')

    def qr_image_preview(self, obj):
        if obj.qr_image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; border: 1px solid #ccc;" />',
                obj.qr_image.url
            )
        return "No QR"
    qr_image_preview.short_description = "QR code"

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width: 100px; height: 100px; object-fit: cover;" />', obj.photo.url)
        return "No photo"
    photo_preview.short_description = "Preview"

    def qr_code_status(self, obj):
        if obj.qr_expires_at and obj.qr_expires_at < timezone.now():
            return "Expired"
        return "Active"
    qr_code_status.short_description = "QR status"

    # search_fields = ('last_name', 'qr_code')
    # list_filter = ('is_active',)
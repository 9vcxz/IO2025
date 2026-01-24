# core/admin.py

from django.contrib import admin
from .models import Employee, EmployeePhoto
from .services.employee_service import EmployeeQRService
from .services.log_service import LogExportService

from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html
from django.urls import path

# Register your models here.


@admin.action(description="Generate new QR codes and validate them for 30 days")
def update_qr_codes(modeladmin, request, queryset):
    for employee in queryset:
        EmployeeQRService.update_qr_code(employee)
    modeladmin.message_user(request, f"Successfuly updates QR codes for {queryset.count()} employees.")

@admin.action(description="Refresh current QR codes for next 30 days")
def refresh_qr_codes(modeladmin, request, queryset):
    for employee in queryset:
        employee.refresh_QR_code()
    modeladmin.message_user(request, f"Successfuly refreshed QR codes for {queryset.count()} employees.")

@admin.action(description="removes employee from db")
def delete_employees(modeladmin, request, queryset):
    for employee in queryset:
        employee.delete_employee()
    modeladmin.message_user(request, f"Successfuly fired {queryset.count()} employees.")

class EmployeePhotoInline(admin.TabularInline):
    model = EmployeePhoto
    extra = 1
    fields = ['image']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    inlines = [EmployeePhotoInline]
    fields = ('first_name', 'last_name',  'is_active')
    list_display = (
        'id',
        'photo_preview', 
        'first_name', 
        'last_name', 
        'is_active',
        'qr_image_preview',
        'qr_expires_at', 
    )

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)

    
    actions = [refresh_qr_codes, update_qr_codes, delete_employees]
    readonly_fields = ('qr_code_str', 'photo_preview', 'qr_image_preview')

    def qr_image_preview(self, obj):
        if obj.qr_code_image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; border: 1px solid #ccc;" />',
                obj.qr_code_image.url
            )
        return "No QR"
    qr_image_preview.short_description = "QR code"

    def photo_preview(self, obj):
        if obj.get_first_photo:
            return format_html('<img src="{}" style="width: 100px; height: 100px; object-fit: cover;" />', obj.get_first_photo.image.url)
        return "No photo"
    photo_preview.short_description = "Photo Preview"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-all-logs/', 
                 self.admin_site.admin_view(self.export_all_logs_view), 
                 name='export_all_logs'),
        ]
        return custom_urls + urls

    def export_all_logs_view(self, request):
        """Widok generujący logi dla WSZYSTKICH pracowników"""
        # Wywołujemy serwis bez przekazywania konkretnego employee
        content = LogExportService.generate_logs_text()
        
        response = HttpResponse(content, content_type='text/plain; charset=utf-8')
        filename = f"pelny_raport_logow_{timezone.now().strftime('%Y%m%d_%H%M')}.txt"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    # def qr_code_status(self, obj):
    #     if obj.qr_expires_at and obj.qr_expires_at < timezone.now():
    #         return "Expired"
    #     return "Active"
    # qr_code_status.short_description = "QR status"

    # search_fields = ('last_name', 'qr_code')
    # list_filter = ('is_active',)
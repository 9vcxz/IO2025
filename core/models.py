# core/models.py

from django.db import models
from django.utils import timezone
from datetime import timedelta
from .services.face_services import FaceService
from django.core.files.base import ContentFile

# Create your models here.
class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    qr_code_str = models.CharField(max_length=255, blank=True, null=True)
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True, verbose_name='QR code image')
    qr_expires_at = models.DateTimeField(null=True, blank=True, verbose_name="QR expiry date")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def get_first_photo(self):
        return self.photos.first()
    
    def add_photo(self, image_stream):

        filename = f"timezone.now().jpg"
        content_file = ContentFile(image_stream.read(), name=filename)

        return EmployeePhoto.objects.create(
            employee=self,
            image=content_file
        )

    def refresh_QR_code(self) -> None:
        self.qr_expires_at = timezone.now() + timedelta(days=30)
        self.save(update_fields=['qr_expires_at'])

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    def delete_employee(self):
        self.delete()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class EmployeePhoto(models.Model):
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='photos'
    )
    image = models.ImageField(upload_to=FaceService.employee_photo_path)
    encoding = models.JSONField(null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.image and not self.encoding:
            encoding_array = FaceService.encode_face_img(self.image)
            if encoding_array is not None:
                self.encoding = list(encoding_array)
            else:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.created_at} - {self.employee.first_name}: {self.employee.last_name}"


class Log(models.Model):
    event_time = models.DateTimeField(auto_now_add=True)
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs'
    )
    access_status = models.BooleanField()
    deny_reason = models.CharField(max_length=200, blank=True, null=True)

    def get_full_report(self):
        date_str = self.event_time.strftime("%d.%m.%Y %H:%M:%S")
        
        status_str = "potwierdzenie" if self.access_status else "odmowa"

        report = (
            f"data zdarzenia: {date_str}\n"
            f"zezwolenie na wejście: {status_str}"
        )

        if self.deny_reason:
            report += f"\nPowód: {self.deny_reason}"

        if self.employee:
            report += f"\nOsoba: {self.employee}"
        else:
            report += "\nOsoba: "

        return report

    def __str__(self):
        name = self.employee.last_name if self.employee else "Unknown"
        return f"{self.event_time} - {name}: {self.access_status}"

class EmployeePermission(models.Model):
    pass

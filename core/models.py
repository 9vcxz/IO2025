# core/models.py

import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.html import format_html
import qrcode
from io import BytesIO
from django.core.files import File
from unidecode import unidecode


# Create your models here.
class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    qr_code = models.CharField(max_length=36, default=uuid.uuid4, unique=True, editable=False)
    qr_expires_at = models.DateTimeField(null=True, blank=True, verbose_name="QR expiry date")

    qr_image = models.ImageField(upload_to='qr_codes/', null=True, blank=True, verbose_name='QR code image')

    def employee_photo_path(instance, filename):
        img_extension = filename.split('.')[-1]
        return "employees_photos/photo_{0}_{1}.{2}".format(
            unidecode(instance.first_name.lower()), 
            unidecode(instance.last_name.lower()), 
            img_extension
        )
    photo = models.ImageField(upload_to=employee_photo_path)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.qr_code = uuid.uuid4()
        
        if not self.qr_expires_at:
            self.qr_expires_at = timezone.now() + timedelta(days=30)

        if self.qr_code != self.__original_qr_code or not self.qr_image:
             self.generate_and_save_qr()

        super().save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_qr_code = self.qr_code

    def generate_and_save_qr(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(str(self.qr_code))
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        # file_name = f"qr_{self.qr_code}.png"

        file_name = f"qr_{unidecode(self.first_name.lower())}_{unidecode(self.last_name.lower())}.png"
        self.qr_image.save(file_name, File(buffer), save=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class SuccessLog(models.Model):
    pass

class FailureLog(models.Model):
    pass



class EmployeePermission(models.Model):
    pass
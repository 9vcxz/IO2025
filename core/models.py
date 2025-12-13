import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.html import format_html
import qrcode
from io import BytesIO
from django.core.files import File


# Create your models here.
class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    qr_code = models.CharField(max_length=36, default=uuid.uuid4, unique=True, editable=False)
    qr_expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Data ważności kodu QR")

    qr_image = models.ImageField(upload_to='qr_codes/', null=True, blank=True, verbose_name='Obrazek QR')

    photo = models.ImageField(upload_to='employees_photos/')

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

    def photo_preview(self):
        if self.photo:
            return format_html('<img src="{}" style="width: 100px; height: 100px; object-fit: cover;" />', self.photo.url)
        return "Brak zdjęcia"
    photo_preview.short_description = "Podgląd"
    
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
        file_name = f"qr_{self.qr_code}.png"
        self.qr_image.save(file_name, File(buffer), save=False)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"
# core/models.py

from django.db import models
from django.utils import timezone
from datetime import timedelta
from .services.face_services import FaceService

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
    
    def add_photo(self, image_file):
        return EmployeePhoto.objects.create(
            employee=self,
            image=image_file
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

    def __str__(self):
        return f"{self.event_time} - {self.employee.last_name}: {self.access_status}"

class EmployeePermission(models.Model):
    pass



    #     if not self.qr_code:
    #         self.qr_code = uuid.uuid4()
    #     if not self.qr_expires_at:
    #         self.qr_expires_at = timezone.now() + timedelta(days=30)
    #     if self.qr_code != self.__original_qr_code or not self.qr_image:
    #          self.generate_and_save_qr()

    #     is_new_photo = False
    #     if self.pk:
    #         old_photo = Employee.objects.get(pk=self.pk).photo
    #         if old_photo != self.photo:
    #             is_new_photo = True
    #     else:
    #         is_new_photo = True

    #     super().save(*args, **kwargs)

    #     if is_new_photo and self.photo:
    #         try:
    #             image = face_recognition.load_image_file(self.photo.path)
    #             encodings = face_recognition.face_encodings(image)

    #             if encodings:
    #                 self.photo_encoding = encodings[0].tolist()
    #                 super().save(update_fields=['photo_encoding'])
    #             else:
    #                 # Do dopisania później
    #                 print("nie funguje")
    #         except Exception as e:
    #             print(f'Encountered error during photo encoding: {e}')

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.__original_qr_code = self.qr_code

    # def generate_and_save_qr(self):
    #     qr = qrcode.QRCode(
    #         version=1,
    #         error_correction=qrcode.constants.ERROR_CORRECT_L,
    #         box_size=10,
    #         border=4,
    #     )

    #     qr.add_data(str(self.qr_code))
    #     qr.make(fit=True)

    #     img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    #     buffer = BytesIO()
    #     img.save(buffer, format="PNG")
    #     # file_name = f"qr_{self.qr_code}.png"

    #     file_name = f"qr_{unidecode(self.first_name.lower())}_{unidecode(self.last_name.lower())}.png"
    #     self.qr_image.save(file_name, File(buffer), save=False)
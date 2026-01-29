#core/services/employee_services.py
from ..models import Employee
from .qr_services import QRCodeService
from django.db import transaction
from django.utils import timezone
from django.core.files.base import ContentFile
from unidecode import unidecode
from datetime import timedelta



class EmployeeService:
    @staticmethod
    def create_employee(first_name, last_name):
        employee = Employee.objects.create(first_name=first_name, last_name=last_name)
        EmployeeQRService.setup_initial_qr(employee)
        return employee
    
    @staticmethod
    def update_qr_code(employee: Employee) -> None:
        EmployeeQRService.update_qr_code(employee)



class EmployeeQRService:
    @staticmethod
    @transaction.atomic
    def setup_initial_qr(employee: Employee):
        qr_str = QRCodeService.setup_initial_qr_str(employee)
        qr_buffer = QRCodeService.generate_qr_img(qr_str)

        file_name = (
            f"qr_{employee.id}_"
            f"{unidecode(employee.first_name.lower())}_"
            f"{unidecode(employee.last_name.lower())}.png"
        )

        employee.qr_code_str = qr_str
        employee.qr_expires_at = timezone.now() + timedelta(days=30)
        employee.qr_code_image.save(
            file_name,
            ContentFile(qr_buffer.getvalue()),
            save=False
        )
        employee.save(update_fields=[
            "qr_code_str",
            "qr_expires_at",
            "qr_code_image"
        ])

    @staticmethod
    @transaction.atomic
    def update_qr_code(employee:Employee) -> None:
        new_qr_string = QRCodeService.update_qr_str()
        employee.qr_expires_at = timezone.now() + timedelta(days=30)

        file_name = f"qr_{str(employee.id)}_{unidecode(employee.first_name.lower())}_{unidecode(employee.last_name.lower())}.png"
        qr_buffer = QRCodeService.generate_qr_img(new_qr_string)

        employee.qr_code_str = new_qr_string
        employee.qr_code_image.save(file_name, ContentFile(qr_buffer.getvalue()), save=False)
        employee.save(update_fields=['qr_code_str', 'qr_expires_at', 'qr_code_image'])
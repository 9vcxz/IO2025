#core/services/qr_services.py
from django.utils import timezone
from django.core.files.base import ContentFile
from typing import TYPE_CHECKING
import uuid
import qrcode
from io import BytesIO
from unidecode import unidecode


if TYPE_CHECKING:
    from core.models import Employee

class QRCodeService:

  @staticmethod
  def generate_qr_img(data: str) -> BytesIO:
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


  @staticmethod
  def setup_initial_qr_str(employee: "Employee") -> str:
    qr_str = unidecode(f"ID: {str(employee.id)},Imie: {employee.first_name} Nazwisko: {employee.last_name}")
    return qr_str

  @staticmethod
  def update_qr_str()-> str:
    return str(uuid.uuid4())
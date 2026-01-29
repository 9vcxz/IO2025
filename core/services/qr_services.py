#core/services/qr_services.py
from django.utils import timezone
from django.core.files.base import ContentFile
import uuid
import qrcode
from io import BytesIO
from unidecode import unidecode


import types


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


  # funkcja testowa do debugowania zeby latwo zobaczyc do ktorego pracownika jest kod qr
  @staticmethod
  def setup_initial_qr_str(employee):
    qr_str = unidecode(f"ID: {str(employee.id)},Imie: {employee.first_name} Nazwisko: {employee.last_name}")
    # qr_str = uuid.uuid4()
    return qr_str

  @staticmethod
  def update_qr_str()-> str:
    return str(uuid.uuid4())
  

  # printy mozna na koniec wywalic sluzyly do debugowania 
  @staticmethod
  def verify_qr(qr_code_str:str):
    """
    metoda wetyfikacji kodow qr przekazanych ze strony skanowania
    Zwraca (employee, error_message, status_code)
    """
    from core.models import Employee, Log

    # sprawdzenie czy qr w ogole się przesłał
    if not qr_code_str:
      print('brak qr kodu z kamery')
      return None, "Nie znaleziono kodu QR spróbuj jeszcze raz", 400
    
    # sprawdzenie czy jest pracownik z tym kodem qr
    try:
      employee = Employee.objects.get(qr_code_str=qr_code_str)
    except Employee.DoesNotExist:
      print('brak qr kodu w bazie')
      return None, "Brak kodu QR w bazie", 404
    
    # Weryfikacja aktywności pracownika i stworzenie logu
    if not employee.is_active:
      Log.objects.create(
          employee=employee,
          access_status=False,
          deny_reason="pracownik nieaktywny"
      )
      return None, "Status jako pracownika jest nieaktywny", 403
    
    # Weryfikacja daty ważności qr kodu
    if employee.qr_expires_at and employee.qr_expires_at < timezone.now():
      Log.objects.create(
          employee=employee,
          access_status=False,
          deny_reason="kod qr wygasl"
      )
      return None, "kod QR wygasł", 403 
    
    # jesli wszystko przejdzie zwracamy poprawny status i pracownika
    return employee, None, 200
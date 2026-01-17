# core/services/face_services.py
import face_recognition
from unidecode import unidecode
import datetime
import logging
from io import BytesIO
import base64
import numpy as np

from PIL import Image # do debugowania

logger = logging.getLogger(__name__)

class FaceService:
    @staticmethod
    def employee_photo_path(instance, filename):
        """
        funkcja zwraca na podstawie imienia i nazwiska pracownika sciezke do jego folderu ze zdjeciami
        """
        ext = filename.split('.')[-1]

        emp_id = instance.employee.id
        first_name = unidecode(instance.employee.first_name.lower())
        last_name = unidecode(instance.employee.last_name.lower())
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"scan_{timestamp}.{ext}"

        return f"employees_photos/{emp_id}_{first_name}_{last_name}/{new_filename}"
    
    @staticmethod
    def encode_face_img(image_stream):
        try:
            image_stream.seek(0)
            face_img = face_recognition.load_image_file(image_stream)
            encodings = face_recognition.face_encodings(face_img)
            
            if not encodings:
                logger.warning(f"Nie znaleziono twarzy na przesłanym zdjęciu.")
                return None
            
            return encodings[0]
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania encodingu: {e}")
            return None
    

    @staticmethod
    def compare_faces(known_face, test_face):
        test_encoding = FaceService.encode_face_img(test_face)
        
        print(f"typ znanej twarzy z bazy{type(known_face)},\n" 
              f"typ porownywalnej twarzy {type(test_encoding)}")
        
        if test_encoding is None:
            return False
        
        results = face_recognition.compare_faces(
        [known_face],
        test_encoding,
        tolerance=0.6
        )

        return results[0]
    
    @staticmethod
    def base64_to_bytesIO(b64_string):
        try:
            if not b64_string: return None
            if ";base64," in b64_string:
                b64_string = b64_string.split(';base64,')[1]
            else:
                b64_string = b64_string
            
            decoded_img = base64.b64decode(b64_string)
            img_stream = BytesIO(decoded_img)
            return img_stream
        except Exception as e:
            logger.error(f"Błąd dekodowania base64: {e}")
            return None


# error_msg, status_code = QRCodeService.verify_qr(qr_code_req)
    @staticmethod
    def verify_photo(employee_id, image_b64):
        from core.models import Employee, Log

        bytes_photo = FaceService.base64_to_bytesIO(image_b64)

        if not bytes_photo:
            return "Serwerowi nie udało się przetworzyć zdjęcia", 400
        
        # do debugowania sprawdza czy twarz sie przeslala
        bytes_photo.seek(0)
        img = Image.open(bytes_photo)
        img.show()
        bytes_photo.seek(0)

        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            Log.objects.create(employee=None,
            access_status=False,
            deny_reason="nie znaleziono pracownika mimo poprawnego kodu qr")

            return f"Nie znaleziono pracownika z ID: {employee_id}", 404
        

        employee_photos = employee.photos.all()
        if not employee_photos.exists():

            Log.objects.create(employee=employee,
            access_status=False,
            deny_reason="pracownik nie posiada zdjecia")

            return "Brak posiadanych zdjec w bazie danych", 404
        
        # sprawdzanie zdjec ze wszystkich posiadanych
        match_found = False
        for photo_obj in employee_photos:
            if photo_obj.encoding:
                known_encoding = np.array(photo_obj.encoding)
                results = FaceService.compare_faces(known_encoding, bytes_photo)
                if results:
                    match_found = True
                    break

        if match_found:
            bytes_photo.seek(0)
            employee.add_photo(bytes_photo)
            Log.objects.create(employee=employee,
            access_status=True)
            return None, 200
        else:
            Log.objects.create(employee=employee,
            access_status=False,
            deny_reason="nie znaleziono pasujacej twarzy w bazie danych")
            return "nie znaleziono pasujacej twarzy w bazie danych", 403
        
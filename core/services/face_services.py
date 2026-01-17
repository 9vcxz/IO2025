import face_recognition
from unidecode import unidecode
import datetime
import logging

logger = logging.getLogger(__name__)

class FaceService:
    @staticmethod
    def employee_photo_path(instance, filename):
        ext = filename.split('.')[-1]
        return (
            f"employees_photos/"
            f"{instance.employee.id}_"
            f"{unidecode(instance.employee.first_name.lower())}_"
            f"{unidecode(instance.employee.last_name.lower())}_"
            f"{datetime.datetime.now()}.{ext}"
        )
    
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
        results = face_recognition.compare_faces([known_face], test_face)
        return results
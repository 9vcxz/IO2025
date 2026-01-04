from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Employee, Log
from django.utils import timezone
from rest_framework.permissions import AllowAny

from .services.face_services import FaceService

# Create your views here.
def scan_site(request):
  return render(request, 'core/scan_site.html')


# TEMP
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
# api test
# tak uzywam printow do debugowania wywalic je pod koniec xd
@method_decorator(csrf_exempt, name='dispatch')
class VerifyQRView(APIView):
    authentication_classes = [] # Usuwa wymóg sesji/tokena
    permission_classes = [AllowAny] # Pozwala każdemu na dostęp

    def post(self, request):
        qr_code_req = request.data.get('qr_code')

        if not qr_code_req:
            print('brak qr kodu z kamery')
            return Response({"status":"error", "message":"No QR code"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.get(qr_code_str=qr_code_req)
        except:
            print('brak qr kodu w bazie')
            return Response({"status":"error", "message":"Unknown QR code"}, status=status.HTTP_404_NOT_FOUND)

        if not employee.is_active:
            print('pracownik nie aktywny')

            Log.create(employee=employee,
                       status=False,
                       deny_reason="pracownik nieaktywny")
            
            return Response({"status":"error", "message":"Employee is not active"}, status=status.HTTP_403_FORBIDDEN)

        if employee.qr_expires_at and employee.qr_expires_at < timezone.now():
            print('qr kod wygasl')

            Log.create(employee=employee,
            status=False,
            deny_reason="kod qr wygasl")
            return Response({"status":"error", "message":"QR code is expired"}, status=status.HTTP_403_FORBIDDEN)

        return Response(
            {
                "status":"success", 
                "message":f"Welcome, {employee.first_name}.",
                "employee_id":f"{employee.id}"
            },
            status=status.HTTP_200_OK
        )


import base64
from PIL import Image
from io import BytesIO
import face_recognition
import numpy as np

@method_decorator(csrf_exempt, name='dispatch')
class VerifyPhotoView(APIView):
    authentication_classes = [] # Usuwa wymóg sesji/tokena
    permission_classes = [AllowAny] # Pozwala każdemu na dostęp
    def post(self, request):
        image_b64_req = request.data.get('img_data')
        employee_id = request.data.get('employee_id')

        try:
            if ";base64," in image_b64_req:
                image_b64 = image_b64_req.split(';base64,')[1]
            else:
                image_b64 = image_b64_req
            
            decoded_img = base64.b64decode(image_b64)
            img_stream = BytesIO(decoded_img)
        except Exception:
            return Response({"status":"error", "message":"Invalid image data"}, status=400)

        # img = Image.open(img_stream)
        # img.show()
        # face_img = face_recognition.load_image_file(img_stream)
        # req_face_encodings = face_recognition.face_encodings(face_img)

        req_face_encodings = FaceService(img_stream)

        if req_face_encodings == None:
            return Response({"status":"error", "message":"No faces found"}, status=status.HTTP_400_BAD_REQUEST)
        
        req_face_encoding = req_face_encodings[0]

        try:
            employee = Employee.objects.get(id=employee_id)
        except:
            Log.create(employee=employee,
            status=False,
            deny_reason="nie znaleziono pracownika mimo poprawnego kodu qr")

            return Response({"status":"error", "message":f"Employee with id: {employee_id} not found"}, status=status.HTTP_404_NOT_FOUND)


        employee_photos = employee.photos.all()
        if not employee_photos.exists():

            Log.create(employee=employee,
            status=False,
            deny_reason="pracownik nie posiada zdjecia")

            return Response({"status":"error", "message":"No photo encoding found in db"}, status=status.HTTP_404_NOT_FOUND)

        match_found = False
        for photo_obj in employee_photos:
            if photo_obj.encoding:
                known_encoding = np.array(photo_obj.encoding)
                results = FaceService.compare_faces(known_encoding, req_face_encoding)
                
                if results[0]:
                    match_found = True
                    break 

        if match_found:
            employee.add_photo(img_stream)

            Log.create(employee=employee,
            status=True)

            return Response({"status":"success", "message":"Success, face match found"}, status=status.HTTP_200_OK)
        else:
            Log.create(employee=employee,
            status=False,
            deny_reason="nie znaleziono pasujacej twrzay w bazie danych")
            return Response({"status":"error", "message":"No face match found"}, status=status.HTTP_403_FORBIDDEN)
        
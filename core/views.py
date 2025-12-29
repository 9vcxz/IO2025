from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Employee
from django.utils import timezone


# Create your views here.
def scan_site(request):
  return render(request, 'core/scan_site.html')


# TEMP
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
# api test
@method_decorator(csrf_exempt, name='dispatch')
class VerifyQRView(APIView):
    def post(self, request):
        qr_code_req = request.data.get('qr_code')

        if not qr_code_req:
            return Response({"status":"error", "message":"No QR code"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.get(qr_code=qr_code_req)
        except:
            return Response({"status":"error", "message":"Unknown QR code"}, status=status.HTTP_404_NOT_FOUND)

        if not employee.is_active:
            return Response({"status":"error", "message":"Employee is not active"}, status=status.HTTP_403_FORBIDDEN)

        if employee.qr_expires_at and employee.qr_expires_at < timezone.now():
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
    def post(self, request):
        image_b64_req = request.data.get('img_data')
        employee_id = request.data.get('employee_id')

        if ";base64," in image_b64_req:
                header, image_b64 = image_b64_req.split(';base64,')

        decoded_img = base64.b64decode(image_b64)
        img_stream = BytesIO(decoded_img)

        # img = Image.open(img_stream)
        # img.show()

        face_img = face_recognition.load_image_file(img_stream)
        req_face_encodings = face_recognition.face_encodings(face_img)

        if len(req_face_encodings) == 0:
            return Response({"status":"error", "message":"No faces found"}, status=status.HTTP_400_BAD_REQUEST)
        
        req_face_encoding = req_face_encodings[0]

        try:
            employee = Employee.objects.get(id=employee_id)
        except:
            return Response({"status":"error", "message":f"Employee with id: {employee_id} not found"}, status=status.HTTP_404_NOT_FOUND)

        if not employee.photo_encoding: 
            return Response({"status":"error", "message":"No photo encoding found in db"}, status=status.HTTP_404_NOT_FOUND)

        known_face_encoding = np.array(employee.photo_encoding)
        results = face_recognition.compare_faces([known_face_encoding], req_face_encoding)

        if not results[0]:
            return Response({"status":"error", "message":"No face match found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"status":"success", "message":"Success, face match found"}, status=status.HTTP_200_OK)
        
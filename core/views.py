from django.shortcuts import render, redirect, get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .services.face_services import FaceService
from .services.qr_services import QRCodeService
from .models import Employee

# Create your views here.
def scan_site(request):
  return render(request, 'core/scan_site.html')


def employee_panel(request, employee_id):
  """Panel pracownika wyświetlany po pomyślnej weryfikacji"""
  employee = get_object_or_404(Employee, id=employee_id)
  return render(request, 'core/employee_panel.html', {'employee': employee})


# TEMP
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
# api test
@method_decorator(csrf_exempt, name='dispatch')
class VerifyQRView(APIView):
    authentication_classes = [] # Usuwa wymóg sesji/tokena
    permission_classes = [AllowAny] # Pozwala każdemu na dostęp

    def post(self, request):
        qr_code_req = request.data.get('qr_code')
        
        # Wywołanie serwisu
        employee, error_msg, status_code = QRCodeService.verify_qr(qr_code_req)

        # kazda niepoprawna weryfikacja przesyla error message 
        if error_msg:
            return Response({"status": "error", "message": error_msg}, status=status_code)
        
        # przy poprawej weryfikacji erro_msg ma byc None i wyslane jest id pracownika do frontu
        return Response({
            "status": "success",
            "message": f"QR zeskanowany pomyslnie znaleziony pracownik {employee.first_name} zaraz nastapi skanowanie twarzy",
            "employee_id": employee.id
        }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class VerifyPhotoView(APIView):
    authentication_classes = [] # Usuwa wymóg sesji/tokena
    permission_classes = [AllowAny] # Pozwala każdemu na dostęp
    def post(self, request):
        image_b64_req = request.data.get('img_data')
        employee_id = request.data.get('employee_id')
        
        # tylko wywolanie funkcji do sprawdzenia zeskanowanego zdjecia twarzy
        # przekaznie id pracownika i zdjecie z frontu w formacie base64
        # error_msg jest tylko przy bledach przy poprawnej weryfikacji wynosi None
        error_msg, status_code = FaceService.verify_photo(employee_id, image_b64_req)

        if error_msg:
            return Response({"status": "error", "message": error_msg}, status=status_code)
        
        return Response({
            "status": "success",
            "message": f"Poprawnie zeskanowano twarz mozna wejsc na teren fabryki",
        }, status=status.HTTP_200_OK)

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
        
        return Response({"status":"success", "message":f"Welcome, {employee.first_name}."}, status=status.HTTP_200_OK)


class VerifyPhotoView(APIView):
    ...
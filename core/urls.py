from django.urls import path
from . import views

urlpatterns = [
    path('scan/', views.scan_site),
    path('employee/<int:employee_id>/', views.employee_panel, name='employee_panel'),
]

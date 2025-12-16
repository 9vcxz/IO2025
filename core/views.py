from django.shortcuts import render

# Create your views here.
def scan_site(request):
  return render(request, 'core/scan_site.html')
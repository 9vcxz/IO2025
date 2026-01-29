# System do wykrywania nadużyć wejść pracowników

## Użyte technologie:
- Django              https://www.djangoproject.com/
- face_recognition    https://github.com/ageitgey/face_recognition
- Instascan           https://github.com/schmich/instascan

## Jak uruchomić:
```
git clone https://github.com/9vcxz/IO2025/
git checkout testing
python3 -m venv .venv
source .venv/bin/activate
pip install setuptools
pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py makemigrations core
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver
```

## Zarządzanie pracownikami
Bazą pracowników zarządzać można z poziomu panelu administracyjnego dostępnego z endpointu ```http://127.0.0.1:8000/admin/```. 
<br>Dodanie pracownika wymaga podanie jego:
- imienia
- nazwiska
- zdjęcia twarzy

Dodanych pracowników można zobaczyć pod ```http://127.0.0.1:8000/admin/core/employee/```. QR kod pracownika zostanie wygenerowany automatycznie. Domyślnie czas jego ważności wygasa po 30 dniach. 

W panelu dostępne są trzy główne akcje:
- usunięcie pracowników
- odświeżenie obecnych kodów QR na następne 30 dni
- wygenerowanie nowych kodów i zatwierdzenie ich na następne 30 dni


## Skanowanie twarzy
Endpoint ze skanowaniem twarzy dostępny jest pod adresem: ```http://127.0.0.1:8000/scan/```. 
<br>Pracownik może zobaczyć podgląd z kamery, oraz komunikat proszący go o przystawienie do kamery swój kod QR. 
<br>Po zeskanowaniu kodu wystąpi jedna z trzech możliwości:
1. Kod QR nie zostanie znaleziony w bazie danych
2. Kod znajduje się w bazie, ale wygasł
3. Kod jest prawidłowy

O wszystkich ewentualnościach pracownik zostanie poinformowany.
<br>Dwie sekundy po dokonaniu skanu kodu, zostanie zrobione zdjęcie twarzy pracownika, które zostanie sprawdzone z referencyjnym znajdującym się w bazie danych. Czas między pokazaniem kodu QR, a ustawieniem się do zdjęcia jest specjalnie krótki, aby ograniczyć nadużycia płynące z ataku prezentacyjnego (pokazanie cudzego zdjęcia do kamery). 
<br>Jeżeli weryfikacja się powiedzie, na ekranie pojawi się profil uwierzytelnionego pracownika, w przeciwnym razie - zostanie poproszony o ponowny skan.


## Logi
Wydarzenia takie jak:
- poprawne wejście pracownika
- podanie kodu QR, który nie znajduje się w bazie danych
- podanie kodu QR, który wygasł
- zeskanowanie twarzy niezgodnej z odpowiadającym jej kodem QR

Są monitorowane i gromadzone. Administrator pod adresem ```http://127.0.0.1:8000/admin/``` może znaleźć zakładkę `Raporty systemowe`, pod którą widnieje przycisk `Pobierz wszystkie logi`. Po kliknięciu rozpocznie się pobranie pliku txt z zebranymi dotychczas wydarzeniami.



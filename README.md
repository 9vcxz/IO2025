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
pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py makemigrations core
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver
```
Na ten moment, aby skanować kod i twarz w /scan, należy wylogować się z panelu admina. Wygenerowany w adminpanelu kod QR wystarczy przystawić do kamery, następnie zdjęcie wysłać przyciskiem.

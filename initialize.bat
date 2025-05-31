if exist .venv (
    rmdir /s /q .venv
)

uv venv .venv -p 3.12

call .venv\Scripts\activate.bat

uv pip install -r requirements.txt

python ./manage.py makemigrations
python ./manage.py migrate

set DJANGO_SUPERUSER_USERNAME=admin
set DJANGO_SUPERUSER_EMAIL=admin@example.com
set DJANGO_SUPERUSER_PASSWORD=admin

python manage.py createsuperuser --noinput
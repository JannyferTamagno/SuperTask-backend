python manage.py migrate --noinput

gunicorn supertask.wsgi:application --bind 0.0.0.0:$PORT
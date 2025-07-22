# Executar migrações (caso necessário)
python manage.py migrate --noinput

# Iniciar o servidor Gunicorn
gunicorn supertask.wsgi:application --bind 0.0.0.0:$PORT
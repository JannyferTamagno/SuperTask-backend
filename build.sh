set -o errexit  # Sair se algum comando falhar

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Executar migrações
python manage.py migrate
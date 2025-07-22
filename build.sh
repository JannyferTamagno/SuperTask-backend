set -o errexit  # Sair se algum comando falhar

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Executar migrações
python manage.py migrate --noinput

# 🧪 EXECUTAR TESTES COM SQLITE
echo "🧪 Executando testes com SQLite..."

# Criar settings temporário para testes
cat > test_settings.py << 'EOF'
from supertask.settings import *

# Sobrescrever apenas o banco para testes
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Desabilitar logs durante testes
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
}
EOF

# Executar testes com configuração SQLite
DJANGO_SETTINGS_MODULE=test_settings python manage.py test --verbosity=2

# Remover arquivo temporário
rm test_settings.py

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

echo "✅ Build concluído com testes executados com sucesso!"
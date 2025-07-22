set -o errexit  # Sair se algum comando falhar

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Executar migrações
python manage.py migrate --noinput

# 🧪 EXECUTAR TESTES (temporário)
echo "🧪 Executando testes..."
python manage.py test --verbosity=2

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

echo "✅ Build concluído com sucesso!"
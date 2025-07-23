set -o errexit  

echo "🚀 Iniciando build..."

echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗃️ Executando migrações..."
python manage.py migrate --noinput

echo "🧪 Executando testes..."
python manage.py test --verbosity=2 --keepdb --noinput

echo "📁 Coletando arquivos estáticos..."  
python manage.py collectstatic --noinput

echo "✅ Build concluído com sucesso!"
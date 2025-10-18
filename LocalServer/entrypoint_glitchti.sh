#!/bin/bash
set -e

echo "📦 Verificando se o banco está disponível..."
until pg_isready -d "${DATABASE_URL}" > /dev/null 2>&1; do
  sleep 2
  echo "⏳ Aguardando PostgreSQL..."
done

echo "🏗️ Rodando migrações..."
python manage.py migrate --noinput

echo "🧩 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "👤 Verificando usuário admin..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email="${GLITCHTIP_ADMIN_EMAIL}").exists():
    User.objects.create_superuser(
        username="${GLITCHTIP_ADMIN_USERNAME}",
        email="${GLITCHTIP_ADMIN_EMAIL}",
        password="${GLITCHTIP_ADMIN_PASSWORD}"
    )
    print("✅ Usuário admin criado com sucesso!")
else:
    print("ℹ️ Usuário admin já existe.")
EOF

echo "📁 Verificando pastas..."
mkdir -p /app/media /app/static

echo "🚀 Iniciando servidor GlitchTip..."
exec gunicorn glitchtip.wsgi:application --bind 0.0.0.0:8000 --workers 4

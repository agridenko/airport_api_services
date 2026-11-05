#!/bin/sh

set -e

echo "Старт початкового скріпту ...."

echo "Очікування готовності PostgreSQL..."
while ! python -c "import socket; s = socket.socket(); s.settimeout(2); s.connect(('airport_db', 5432))" > /dev/null 2>&1; do
    echo "   База даних ще не готова, чекаємо 2 секунди..."
    sleep 2
done
echo "PostgreSQL готовий!"

#Застосовуємо міграції (тільки якщо є нові)
echo "Виконання міграцій..."
python manage.py migrate --noinput

#Збираємо статичні файли (для проду)
echo "Збирання статичних файлів..."
python manage.py collectstatic --noinput || true

# Створюємо суперкористувача, якщо його немає
echo "Перевірка суперкористувача..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email="admin@example.com").exists():
    User.objects.create_superuser("admin@example.com", "admin_123456")
    print("Створено суперкористувача")
else:
    print("Суперкористувач уже існує")
EOF

echo "Початковий скрипт завершено"

# Запускаємо основну команду (наприклад, runserver або gunicorn)
exec "$@"
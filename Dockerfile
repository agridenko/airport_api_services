# Використовуємо офіційний образ Python
FROM python:3.12-slim

# Встановлюємо змінні оточення
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Встановлюємо робочу директорію
WORKDIR /app

# Встановлюємо системні залежності для PostgreSQL
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        libpq-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо requirements і встановлюємо залежності
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копіюємо весь код проекту
COPY . .

# Копіюємо entrypoint скрипт
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Створюємо директорії для статичних файлів
RUN mkdir -p /app/staticfiles /app/media

EXPOSE 8000

# Встановлюємо entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Команда за замовчуванням
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

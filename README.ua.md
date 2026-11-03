# ✈️ Airport Flight System API

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.14-red?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-19_passing-brightgreen)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

> **Повнофункціональна REST API система для управління авіарейсами, бронювання квитків та відстеження маршрутів.**

---

## 📋 Зміст

- [Про проект](#-про-проект)
- [Основні можливості](#-основні-можливості)
- [Технології](#-технології)
- [Архітектура бази даних](#-архітектура-бази-даних)
- [Швидкий старт](#-швидкий-старт)
- [API Документація](#-api-документація)
- [Тестування](#-тестування)
- [Безпека та права доступу](#-безпека-та-права-доступу)
- [Автор](#-автор)

---

## 🎯 Про проект

**Airport Flight System** — це сучасна REST API система, розроблена для управління авіарейсами та бронювання квитків. Проект демонструє best practices розробки на Django REST Framework з акцентом на продуктивність, безпеку та масштабованість.

### Ключові особливості реалізації:

- 🚀 **Повна Docker-ізація** з автоматичними міграціями та ініціалізацією
- 🔒 **Role-Based Access Control (RBAC)** — гнучка система прав доступу
- ⚡ **Оптимізовані запити** — використання `select_related` та `prefetch_related` для усунення N+1 проблеми
- 💰 **Динамічне ціноутворення** — автоматичний розрахунок вартості квитків на основі відстані маршруту
- 🧪 **Повне тестове покриття** — 19 тестів, що покривають всі критичні сценарії
- 📊 **Swagger/OpenAPI документація** — інтерактивна документація API

---

## ✨ Основні можливості

### 🛫 Управління рейсами
- Створення та управління маршрутами між аеропортами
- Планування рейсів з прив'язкою до літаків та екіпажу
- Відстеження часу вильоту та прибуття
- Фільтрація рейсів за маршрутом, датою та літаком

### 🎫 Бронювання квитків
- Автоматичний розрахунок вартості квитка на основі відстані
- Перевірка доступності місць у реальному часі
- Валідація рядів та місць відповідно до конфігурації літака
- Захист від подвійного бронювання одного місця

### 👥 Управління користувачами
- Реєстрація та авторизація користувачів
- Ізоляція даних: користувачі бачать тільки свої замовлення
- Адмін-панель для управління довідниками (аеропорти, літаки, маршрути)

### 📈 Аналітика та звіти
- Перегляд доступних місць на кожному рейсі
- Фільтрація майбутніх рейсів
- Пошук за назвою аеропорту, міста, типу літака

---

## 🛠️ Технології

### Backend
- **Python 3.12** — мова програмування
- **Django 6.1.2** — веб-фреймворк
- **Django REST Framework 3.18.3** — створення REST API
- **PostgreSQL 15** — реляційна база даних
- **psycopg** — адаптер PostgreSQL для Python

### Інфраструктура
- **Docker** — контейнеризація
- **Docker Compose** — оркестрація контейнерів
- **Gunicorn** — WSGI сервер для продакшну (опціонально)

### Документація та тестування
- **drf-yasg** — генерація Swagger/OpenAPI документації
- **Django Debug Toolbar** — профілювання та відладка
- **pytest-django** — тестування API

### Додаткові бібліотеки
- **django-filter** — фільтрація запитів
- **python-decouple** — управління змінними оточення
- **Pillow** — обробка зображень (якщо потрібно)

---

## 🗄️ Архітектура бази даних

### Моделі даних

| Модель | Опис | Ключові поля |
|--------|------|--------------|
| **Airport** | Аеропорт | name, closest_big_city |
| **AirplaneType** | Тип літака | name |
| **Airplane** | Літак | name, rows, seats_in_row, airplane_type |
| **Route** | Маршрут | source, destination, distance |
| **Flight** | Рейс | route, airplane, departure_time, arrival_time, crew |
| **Crew** | Член екіпажу | first_name, last_name |
| **Order** | Замовлення | user, created_at |
| **Ticket** | Квиток | flight, order, row, seat, price |

### Зв'язки між моделями

- **Airport** ←→ **Route**: One-to-Many (source/destination)
- **Route** ←→ **Flight**: One-to-Many
- **Airplane** ←→ **Flight**: One-to-Many
- **Flight** ←→ **Crew**: Many-to-Many
- **Flight** ←→ **Ticket**: One-to-Many
- **Order** ←→ **Ticket**: One-to-Many
- **User** ←→ **Order**: One-to-Many

---

## 🚀 Швидкий старт

### Вимоги

- **Docker** (20.10+)
- **Docker Compose** (2.0+)
- **Git**

### 1. Клонувати репозиторій

```bash
git clone https://github.com/yourusername/airport-flight-system.git
cd airport-flight-system
```

### 2. Налаштувати змінні оточення
#### Скопіювати шаблон .env файлу
```bash
cp .env.example .env
```

### 3. Запустити проект
```bash
# Зібрати та запустити контейнери
docker-compose up --build

# Або запустити у фоновому режимі
docker-compose up -d --build
```

### 4. Створити суперкористувача (опціонально)
```bash
# Контейнер автоматично створює адміна з credentials:
# Username: admin
# Email: admin@example.com
# Password: admin_123456

# Або створити власного суперкористувача:
docker-compose exec web python manage.py createsuperuser
```

### 5. Відкрити додаток
- API Root: http://localhost:8000/api/
- Admin Panel: http://localhost:8000/admin/
- Swagger Docs: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/


## 📚 API Документація
- [OpenAPI Specification](http://localhost:8000/api/schema/openapi.yaml)
- [ReDoc](http://localhost:8000/api/redoc/)
- [Swagger UI](http://localhost:8000/api/docs/)


## 🧪 Тестування
#### Проект має повне тестове покриття з 19 тестами, які перевіряють:
- ✅ CRUD операції для всіх моделей
- ✅ Фільтрацію та пошук
- ✅ Кастомні actions (available_seats, upcoming, from_airport)
- ✅ Права доступу (RBAC)
- ✅ Ізоляцію даних користувачів
- ✅ Валідацію бізнес-логіки (ціна, місця, час)
- ✅ Обробку помилок

#### Запуск тестів
```bash
# Запустити всі тести
docker-compose run --rm web python manage.py test

# Запустити тести з детальним виводом
docker-compose run --rm web python manage.py test flights -v 2
```

## 🔒 Безпека та права доступу

### Role-Based Access Control (RBAC)
#### Система використовує три рівні доступу:
#### 1. Публічний доступ (AllowAny)
- Перегляд аеропортів
- Перегляд типів літаків
- Перегляд літаків
- Перегляд маршрутів
- Перегляд рейсів
- Перегляд екіпажу

#### 2. Авторизований користувач (IsAuthenticated)
- Створення замовлень
- Перегляд власних замовлень
- Додавання квитків до власних замовлень
- Перегляд власних квитків

#### 3. Адміністратор (IsAdminUser / IsStaff)
- CRUD операції з аеропортами
- CRUD операції з літаками
- CRUD операції з маршрутами
- CRUD операції з рейсами
- CRUD операції з екіпажем
- Перегляд всіх замовлень та квитків

### Ізоляція даних
- **Користувачі** бачать тільки свої замовлення та квитки
- **Адміністратори** бачать всі дані в системі
- **Спроба доступу** до чужих даних повертає 404 Not Found

### Валідація та захист
- ✅ Автоматичний розрахунок ціни квитка (не можна маніпулювати)
- ✅ Перевірка доступності місць перед бронюванням
- ✅ Валідація рядів та місць відповідно до конфігурації літака
- ✅ Захист від подвійного бронювання одного місця
- ✅ Перевірка часу вильоту/прибуття (не можна створити рейс у минулому)
- ✅ CSRF захист для сесійної авторизації
- ✅ Rate limiting (опціонально, через Django REST Framework throttling)


## 👨‍💻 Автор
**Alexey Hridenko**
- **GitHub:** https://github.com/agridenko
- **Email:** agridenko@gmail.com
- **LinkedIn:** https://www.linkedin.com/in/alexey-hridenko-243682165/
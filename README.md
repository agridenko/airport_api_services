# ✈️ Airport Flight System API

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.14-red?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-19_passing-brightgreen)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

🇺🇦 [Read in Ukrainian](README.ua.md)

> **A full-featured REST API system for managing flights, booking tickets, and tracking routes.**

---

## 📋 Table of Contents

- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Technologies](#-technologies)
- [Database Architecture](#-database-architecture)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Security and Permissions](#-security-and-permissions) access](#-security-and-access-rights)
- [Author](#-author)

---

## 🎯 About the Project

**Airport Flight System** is a modern REST API system designed for managing flights and booking tickets. The project demonstrates best practices for development using Django REST Framework, with a focus on performance, security, and scalability. ### Key Implementation Features:

- 🚀 **Full Dockerization** with automated migrations and initialization
- 🔒 **Role-Based Access Control (RBAC)** — a flexible access rights system
- ⚡ **Optimized Queries** — utilization of `select_related` and `prefetch_related` to eliminate the N+1 problem
- 💰 **Dynamic Pricing** — automated ticket cost calculation based on route distance
- 🧪 **Comprehensive Test Coverage** — 19 tests covering all critical scenarios
- 📊 **Swagger/OpenAPI Documentation** — interactive API documentation

---

## ✨ Core Capabilities

### 🛫 Flight Management
- Creation and management of routes between airports
- Flight scheduling, linked to specific aircraft and crew
- Tracking of departure and arrival times
- Filtering of flights by route, date, and aircraft

### 🎫 Ticket Booking
- Automated ticket cost calculation based on distance
- Real-time seat availability checks
- Validation of rows and seats according to aircraft configuration
- Prevention of double-booking for the same seat

### 👥 User Management
- User registration and authorization
- Data isolation: users can only view their own bookings
- Admin panel for managing reference data (airports, aircraft, routes)

### 📈 Analytics and Reporting
- Viewing available seats on each flight
- Filtering of upcoming flights
- Search by airport name, city, or aircraft type

---

## 🛠️ Technologies

### Backend
- **Python 3.12** — programming language
- **Django 6.1.2** — web framework
- **Django REST Framework 3.18.3** — for building REST APIs
- **PostgreSQL 15** — relational database
- **psycopg** — PostgreSQL adapter for Python

### Infrastructure
- **Docker** — containerization
- **Docker Compose** — container orchestration
- **Gunicorn** — WSGI server for production (optional)

### Documentation and Testing
- **drf-yasg** — Swagger/OpenAPI documentation generation
- **Django Debug Toolbar** — profiling and debugging
- **pytest-django** — API testing

### Additional Libraries
- **django-filter** — query filtering
- **python-decouple** — environment variable management
- **Pillow** — image processing (if needed)

---

## 🗄️ Database Architecture

### Data Models

| Model | Description | Key Fields |
|-------|-------------|------------|
| **Airport** | Airport | name, closest_big_city |
| **AirplaneType** | Aircraft type | name |
| **Airplane** | Aircraft | name, rows, seats_in_row, airplane_type |
| **Route** | Route | source, destination, distance |
| **Flight** | Flight | route, airplane, departure_time, arrival_time, crew |
| **Crew** | Crew member | first_name, last_name |
| **Order** | Order | user, created_at |
| **Ticket** | Ticket | flight, order, row, seat, price |

### Relationships Between Models

- **Airport** ←→ **Route**: One-to-Many (source/destination)
- **Route** ←→ **Flight**: One-to-Many
- **Airplane** ←→ **Flight**: One-to-Many
- **Flight** ←→ **Crew**: Many-to-Many
- **Flight** ←→ **Ticket**: One-to-Many
- **Order** ←→ **Ticket**: One-to-Many
- **User** ←→ **Order**: One-to-Many

---

## 🚀 Quick Start

### Requirements

- **Docker** (20.10+)
- **Docker Compose** (2.0+)
- **Git**

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/airport-flight-system.git
cd airport-flight-system
```

### 2. Configure environment variables
#### Copy the .env file template
```bash
cp .env.example .env
```

### 3. Run the project
```bash
# Build and run
...the containers
docker-compose up --build

# Or run in the background
docker-compose up -d --build
```

### 4. Create a superuser (optional)
```bash
# The container automatically creates an admin with the following credentials:
# Username: admin
# Email: admin@example.com
# Password: admin_123456

# Or create your own superuser:
docker-compose exec web python manage.py createsuperuser
```

### 5. Access the application
- API Root: http://localhost:8000/api/
- Admin Panel: http://localhost:8000/admin/
- Swagger Docs: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/


## 📚 API Documentation
- [OpenAPI Specification](http://localhost:8000/api/schema/openapi.yaml)
- [ReDoc](http://localhost:8000/api/redoc/)
- [Swagger UI](http://localhost:8000/api/docs/)


## 🧪 Testing
#### The project has full test coverage with 19 tests verifying:
- ✅ CRUD operations for all models
- ✅ Filtering and search
- ✅ Custom actions (available_seats, upcoming, from_airport)
- ✅ Access rights (RBAC)
- ✅ User data isolation
- ✅ Business logic validation (price, seats, time)
- ✅ Error handling

#### Running tests
```bash
# Run all tests
docker-compose run --rm web python manage.py test

# Run tests with detailed output
output
docker-compose run --rm web python manage.py test flights -v 2
```

## 🔒 Security and Access Control

### Role-Based Access Control (RBAC)
#### The system employs three access levels:
#### 1. Public Access (AllowAny)
- View airports
- View aircraft types
- View aircraft
- View routes
- View flights
- View crew

#### 2. Authenticated User (IsAuthenticated)
- Create orders
- View own orders
- Add tickets to own orders
- View own tickets

#### 3. Administrator (IsAdminUser / IsStaff)
- CRUD operations for airports
- CRUD operations for aircraft
- CRUD operations for routes
- CRUD operations for flights
- CRUD operations for crew
- View all orders and tickets

### Data Isolation
- **Users** can only see their own orders and tickets
- **Administrators** can see all data in the system
- **Attempts to access** data belonging to other users result in a 404 Not Found error

### Validation and Protection
- ✅ Automatic ticket price calculation (cannot be manipulated)
- ✅ Seat availability check prior to booking
- ✅ Validation of rows and seats based on aircraft configuration
- ✅ Prevention of double-booking for the same seat
- ✅ Departure/arrival time verification (cannot create a flight in the past)
- ✅ CSRF protection for session-based authentication
- ✅ Rate limiting (optionally, via Django REST Framework throttling)


## 👨‍💻 Author
**Alexey Hridenko**
- **GitHub:** https://github.com/agridenko
- **Email:** agridenko@gmail.com
- **LinkedIn:** https://www.linkedin.com/in/alexey-hridenko-243682165/
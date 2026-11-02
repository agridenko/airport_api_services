from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from flights.models import (
    Airport,
    AirplaneType,
    Airplane,
    Route,
    Flight,
    Crew,
    Order,
    Ticket,
)

User = get_user_model()

# Вимикаємо тротлінг для стабільності тестів
REST_FRAMEWORK_NO_THROTTLE = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {},
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": 10,
}


@override_settings(REST_FRAMEWORK=REST_FRAMEWORK_NO_THROTTLE)
class BaseFlightsAPITestCase(APITestCase):
    """Спільна підготовка даних і клієнтів для API-тестів."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
        )
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            is_staff=True,
        )

        self.airport_kyiv = Airport.objects.create(name="Boryspil", closest_big_city="Kyiv")
        self.airport_lviv = Airport.objects.create(name="Lviv International", closest_big_city="Lviv")
        self.airport_odesa = Airport.objects.create(name="Odesa International", closest_big_city="Odesa")

        self.airplane_type = AirplaneType.objects.create(name="Boeing 737")
        self.airplane_type_other = AirplaneType.objects.create(name="Airbus A320")

        self.airplane = Airplane.objects.create(
            name="UR-PSA", rows=10, seats_in_row=6, airplane_type=self.airplane_type
        )
        self.airplane_other = Airplane.objects.create(
            name="UR-AAA", rows=5, seats_in_row=4, airplane_type=self.airplane_type_other
        )

        self.route = Route.objects.create(source=self.airport_kyiv, destination=self.airport_lviv, distance=540)
        self.route_other = Route.objects.create(source=self.airport_lviv, destination=self.airport_odesa, distance=620)

        self.crew_member = Crew.objects.create(first_name="Ivan", last_name="Pilot")
        self.crew_member_2 = Crew.objects.create(first_name="Olena", last_name="Navigator")

        now = timezone.now()
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=now + timedelta(days=2),
            arrival_time=now + timedelta(days=2, hours=1, minutes=20),
        )
        self.flight.crew.add(self.crew_member)

        self.past_flight = Flight.objects.create(
            route=self.route_other,
            airplane=self.airplane_other,
            departure_time=now - timedelta(days=1),
            arrival_time=now - timedelta(days=1) + timedelta(hours=1),
        )

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)


class AirportApiTests(BaseFlightsAPITestCase):
    def test_list_airports_public(self):
        """Аеропорти можуть переглядати всі (публічний доступ)"""
        url = reverse("flights:airport-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_create_airport_requires_admin(self):
        """Створити аеропорт може тільки адмін"""
        url = reverse("flights:airport-list")
        payload = {"name": "Kharkiv International", "closest_big_city": "Kharkiv"}

        # 1. Без авторизації
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 2. Звичайний користувач
        self.authenticate(self.user)
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Адмін
        self.authenticate(self.admin)
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Airport.objects.count(), 4)

    def test_update_and_delete_airport_requires_admin(self):
        """Оновлювати та видаляти аеропорт може тільки адмін"""
        url = reverse("flights:airport-detail", args=[self.airport_odesa.id])

        # Спроба звичайного користувача
        self.authenticate(self.user)
        response = self.client.patch(url, {"closest_big_city": "Odesa City"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Спроба адміна
        self.authenticate(self.admin)
        response = self.client.patch(url, {"closest_big_city": "Odesa City"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Airport.objects.filter(id=self.airport_odesa.id).exists())


class AirplaneTypeApiTests(BaseFlightsAPITestCase):
    def test_list_and_create_airplane_type(self):
        url = reverse("flights:airplane-type-list")

        # Читання публічне
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Створення тільки для адміна
        self.authenticate(self.admin)
        response = self.client.post(url, {"name": "Embraer E190"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AirplaneApiTests(BaseFlightsAPITestCase):
    def test_list_airplanes(self):
        url = reverse("flights:airplane-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        airplane_data = next(
            item for item in response.data["results"] if item["id"] == self.airplane.id
        )
        self.assertEqual(airplane_data["total_seats"], 60)

    def test_create_airplane_requires_admin(self):
        url = reverse("flights:airplane-list")
        payload = {
            "name": "UR-NEW",
            "rows": 20,
            "seats_in_row": 6,
            "airplane_type_id": self.airplane_type.id,
        }

        self.authenticate(self.admin)
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["total_seats"], 120)


class RouteApiTests(BaseFlightsAPITestCase):
    def test_list_routes(self):
        url = reverse("flights:route-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        route_data = next(
            item for item in response.data["results"] if item["id"] == self.route.id
        )
        self.assertEqual(route_data["source"]["name"], "Boryspil")

    def test_create_route_requires_admin(self):
        url = reverse("flights:route-list")
        payload = {
            "source_id": self.airport_kyiv.id,
            "destination_id": self.airport_odesa.id,
            "distance": 700,
        }
        self.authenticate(self.admin)
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class FlightApiTests(BaseFlightsAPITestCase):
    def test_list_flights(self):
        url = reverse("flights:flight-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        flight_data = next(
            item for item in response.data["results"] if item["id"] == self.flight.id
        )
        self.assertEqual(flight_data["available_seats"], 60)

    def test_create_flight_requires_admin(self):
        url = reverse("flights:flight-list")
        departure = timezone.now() + timedelta(days=5)
        arrival = departure + timedelta(hours=2)
        payload = {
            "route_id": self.route.id,
            "airplane_id": self.airplane.id,
            "departure_time": departure.isoformat(),
            "arrival_time": arrival.isoformat(),
            "crew_ids": [self.crew_member.id, self.crew_member_2.id],
        }

        self.authenticate(self.admin)
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flight.objects.count(), 3)

    def test_available_seats_action(self):
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(order=order, flight=self.flight, row=1, seat=1)

        url = reverse("flights:flight-available-seats", args=[self.flight.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_available"], 59)


class CrewApiTests(BaseFlightsAPITestCase):
    def test_list_and_create_crew(self):
        url = reverse("flights:crew-list")

        # Читання публічне
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Створення тільки для адміна
        self.authenticate(self.admin)
        response = self.client.post(
            url, {"first_name": "Petro", "last_name": "Steward"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class OrderApiTests(BaseFlightsAPITestCase):
    def test_orders_require_authentication(self):
        url = reverse("flights:order-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_and_list_own_orders(self):
        self.authenticate(self.user)
        url = reverse("flights:order-list")

        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id = response.data["id"]

        # Створюємо чуже замовлення, щоб перевірити ізоляцію
        Order.objects.create(user=self.other_user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)  # Бачимо тільки своє
        self.assertEqual(response.data["results"][0]["id"], order_id)

    def test_add_ticket_to_order(self):
        self.authenticate(self.user)
        order = Order.objects.create(user=self.user)
        url = reverse("flights:order-add-ticket", args=[order.id])
        payload = {"flight_id": self.flight.id, "row": 2, "seat": 3}

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["row"], 2)

        expected_price = Decimal("104.00")
        self.assertEqual(Decimal(response.data["price"]), expected_price)

    def test_add_ticket_invalid_seat_fails(self):
        """Перевірка валідації неіснуючого місця"""
        self.authenticate(self.user)
        order = Order.objects.create(user=self.user)
        url = reverse("flights:order-add-ticket", args=[order.id])

        # Літак має 10 рядів і 6 місць. 999 має викликати помилку.
        response = self.client.post(
            url,
            {"flight_id": self.flight.id, "row": 999, "seat": 999},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("non_field_errors", response.data)
        self.assertIn("не існує", str(response.data["non_field_errors"]))


class TicketApiTests(BaseFlightsAPITestCase):
    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(order=self.order, flight=self.flight, row=3, seat=2)

        other_order = Order.objects.create(user=self.other_user)
        self.other_ticket = Ticket.objects.create(order=other_order, flight=self.flight, row=4, seat=1)

    def test_tickets_require_authentication(self):
        url = reverse("flights:ticket-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_sees_only_own_tickets(self):
        self.authenticate(self.user)
        url = reverse("flights:ticket-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.ticket.id)

    def test_retrieve_foreign_ticket_forbidden(self):
        self.authenticate(self.user)
        url = reverse("flights:ticket-detail", args=[self.other_ticket.id])
        response = self.client.get(url)

        # Має бути 404, бо get_queryset фільтрує по user, і об'єкт не знайдено
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

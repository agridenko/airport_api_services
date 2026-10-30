from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from airport_flight_system import settings


class Airport(models.Model):
    """Airport model."""
    name = models.CharField(
        max_length=255,
        verbose_name="Назва",
        unique=True,
    )
    closest_big_city = models.CharField(
        max_length=255,
        verbose_name="Найближче велике місто",
    )

    class Meta:
        verbose_name = "Аеропорт"
        verbose_name_plural = "Аеропорти"

    def __str__(self):
        return f"{self.name} ({self.closest_big_city})"


class AirplaneType(models.Model):
    """Тип літака"""
    name = models.CharField(
        max_length=255,
        verbose_name="Назва",
    )

    class Meta:
        verbose_name = "Тип літака"
        verbose_name_plural = "Типи літаків"

    def __str__(self):
        return self.name


class Airplane(models.Model):
    """Літак"""
    name = models.CharField(
        max_length=255,
        verbose_name="Назва",
    )
    rows = models.IntegerField(
        verbose_name="Кількість рядів",
    )
    seats_in_row = models.IntegerField(
        verbose_name="Кількість місць у ряду",
    )
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes",
        verbose_name="Тип літака",
    )

    class Meta:
        verbose_name = "Літак"
        verbose_name_plural = "Літаки"

    def __str__(self):
        return f"Airplane: {self.name} (Type ID: {self.airplane_type_id})"

    @property
    def total_seats(self):
        """Загальна кількість місць у літаку"""
        return self.rows * self.seats_in_row


class Route(models.Model):
    """Маршрут між двома аеропортами"""
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="source_routes",
        verbose_name="Початковий аеропорт"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="destination_routes",
        verbose_name="Кінцевий аеропорт"
    )
    distance = models.IntegerField(
        verbose_name="Відстань",
    )

    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршрути"

    def __str__(self):
        return f"Route {self.source_id} -> {self.destination_id} ({self.distance} km)"

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Аеропорти не можуть бути однаковими.")


class Flight(models.Model):
    """Рейс переліту"""
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights",
        verbose_name="Маршрут"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights",
        verbose_name="Літак",
    )
    departure_time = models.DateTimeField(
        verbose_name="Час відправлення",
    )
    arrival_time = models.DateTimeField(
        verbose_name="Час прибуття",
    )
    crew = models.ManyToManyField(
        "Crew",
        related_name="flights",
        blank=True,
        verbose_name="Екіпаж",
    )

    class Meta:
        verbose_name = "Рейс"
        verbose_name_plural = "Рейси"
        ordering = ["departure_time"]

    def __str__(self):
        return f"Flight #{self.id} ({self.departure_time.strftime('%Y-%m-%d %H:%M')})"


    def clean(self):
        if self.departure_time < timezone.now():
            raise ValidationError("Вибірка рейсу не може бути в минулому.")

        if self.arrival_time <= self.departure_time:
            raise ValidationError("Час прибуття не може бути раніше часу відправлення.")


class Crew(models.Model):
    """Екіпаж на рейсі"""
    first_name = models.CharField(
        max_length=255,
        verbose_name="Ім'я",
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name="Прізвище",
    )

    class Meta:
        verbose_name = "Член екіпажу"
        verbose_name_plural = "Екіпаж"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    """Замовлення на рейс"""
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата та час замовлення",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Користувач",
    )

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Замовлення {self.id} для {self.user.first_name} {self.user.last_name} ({self.user.email})"

    @property
    def total_cost(self):
        """Загальна вартість замовлення"""
        return sum(ticket.price for ticket in self.tickets.all())


class Ticket(models.Model):
    """Білет на рейс"""
    row = models.IntegerField(
        verbose_name="Ряд"
    )
    seat = models.IntegerField(
        verbose_name="Місце"
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets",
        verbose_name="Рейс"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets",
        verbose_name="Замовлення"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Ціна",
        null=True,
        blank=True
    )

    def calculate_price(self):
        base_price = 50
        distance_multiplier = self.flight.route.distance * 0.1
        return base_price + distance_multiplier

    class Meta:
        verbose_name = "Квиток"
        verbose_name_plural = "Квитки"
        unique_together = ("row", "seat", "flight")
        ordering = ["flight", "row", "seat"]

    def __str__(self):
        return (f"Ticket {self.flight.route.source.name}->"
                f"{self.flight.route.destination.name} "
                f"(Row {self.row}, Seat {self.seat})")

    @staticmethod
    def validate_ticket(row, seat, flight):
        if row > flight.airplane.rows:
            raise ValidationError(f"Ряд {row} не існує в цьому літаку")
        if seat > flight.airplane.seats_in_row:
            raise ValidationError(f"Місце {seat} не існує в цьому рядку")

    def clean(self):
        Ticket.validate_ticket(self.row, self.seat, self.flight)

    def save(self, *args, **kwargs):
        """Записуэмо ціну квитка пристворені з разрахунку"""
        if not self.price:
            base_price = Decimal("50.00")
            # Перевіряємо, чи є маршрут і відстань, щоб не було помилок
            if self.flight.route and self.flight.route.distance:
                distance_multiplier = Decimal(str(self.flight.route.distance)) * Decimal("0.1")
                self.price = base_price + distance_multiplier
            else:
                self.price = base_price

        return super().save(*args, **kwargs)

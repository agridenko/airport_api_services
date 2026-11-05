from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Airport(models.Model):
    """Airport model."""
    name = models.CharField(
        max_length=255,
        verbose_name="Name",
        unique=True,
    )
    closest_big_city = models.CharField(
        max_length=255,
        verbose_name="Closest big city",
    )

    class Meta:
        verbose_name = "Airport"
        verbose_name_plural = "Airports"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.closest_big_city})"


class AirplaneType(models.Model):
    """Airplane type model."""
    name = models.CharField(
        max_length=255,
        verbose_name="Name",
    )

    class Meta:
        verbose_name = "Airplane type"
        verbose_name_plural = "Airplane types"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Airplane(models.Model):
    """Airplane model."""
    name = models.CharField(
        max_length=255,
        verbose_name="Name",
    )
    rows = models.IntegerField(
        verbose_name="Rows count",
    )
    seats_in_row = models.IntegerField(
        verbose_name="Seats per row",
    )
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes",
        verbose_name="Airplane type",
    )

    class Meta:
        verbose_name = "Airplane"
        verbose_name_plural = "Airplanes"
        ordering = ["name"]

    def __str__(self):
        return f"Airplane: {self.name} (Type ID: {self.airplane_type_id})"

    @property
    def total_seats(self):
        """Return the total number of seats in the airplane."""
        return self.rows * self.seats_in_row


class Route(models.Model):
    """Route between two airports."""
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="source_routes",
        verbose_name="Source airport"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="destination_routes",
        verbose_name="Destination airport"
    )
    distance = models.IntegerField(
        verbose_name="Distance",
    )

    class Meta:
        verbose_name = "Route"
        verbose_name_plural = "Routes"
        ordering = ["id"]

    def __str__(self):
        return (
            f"Route {self.source_id} -> {self.destination_id}"
            f" ({self.distance} km)"
        )

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Airports cannot be the same.")


class Flight(models.Model):
    """Flight model."""
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights",
        verbose_name="Route"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights",
        verbose_name="Airplane",
    )
    departure_time = models.DateTimeField(
        verbose_name="Departure time",
    )
    arrival_time = models.DateTimeField(
        verbose_name="Arrival time",
    )
    crew = models.ManyToManyField(
        "Crew",
        related_name="flights",
        blank=True,
        verbose_name="Crew",
    )

    class Meta:
        verbose_name = "Flight"
        verbose_name_plural = "Flights"
        ordering = ["departure_time"]

    def __str__(self):
        return (
            f"Flight #{self.id} "
            f"({self.departure_time.strftime('%Y-%m-%d %H:%M')})"
        )

    def clean(self):
        if self.departure_time < timezone.now():
            raise ValidationError(
                "Flight departure time cannot be in the past."
            )

        if self.arrival_time <= self.departure_time:
            raise ValidationError(
                "Arrival time cannot be earlier than departure time."
            )


class Crew(models.Model):
    """Crew member model."""
    first_name = models.CharField(
        max_length=255,
        verbose_name="First name",
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name="Last name",
    )

    class Meta:
        verbose_name = "Crew member"
        verbose_name_plural = "Crew members"
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    """Order model."""
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created at",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="User",
    )

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} (User ID: {self.user_id})"

    @property
    def total_cost(self):
        """Return the total order cost with a fallback for DB annotations."""
        if hasattr(self, "total_order_cost"):
            return self.total_order_cost or 0
        return sum(ticket.price for ticket in self.tickets.all())


class Ticket(models.Model):
    """Ticket model."""
    row = models.IntegerField(
        verbose_name="Row"
    )
    seat = models.IntegerField(
        verbose_name="Seat"
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets",
        verbose_name="Flight"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets",
        verbose_name="Order"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Price",
        null=True,
        blank=True
    )

    def calculate_price(self):
        base_price = 50
        distance_multiplier = self.flight.route.distance * 0.1
        return base_price + distance_multiplier

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        unique_together = ("row", "seat", "flight")
        ordering = ["flight", "row", "seat"]

    def __str__(self):
        return f"Ticket {self.id} for {self.flight}"

    @staticmethod
    def validate_ticket(row, seat, flight):
        if row > flight.airplane.rows:
            raise ValidationError(
                f"Row {row} does not exist on this airplane."
            )
        if seat > flight.airplane.seats_in_row:
            raise ValidationError(
                f"Seat {seat} does not exist in this row."
            )

    def clean(self):
        Ticket.validate_ticket(self.row, self.seat, self.flight)

    def save(self, *args, **kwargs):
        """Set the ticket price automatically when the ticket is created."""
        if not self.price:
            base_price = Decimal("50.00")
            # Check route and distance to avoid errors.
            if self.flight.route and self.flight.route.distance:
                distance_multiplier = Decimal(
                    str(self.flight.route.distance)
                ) * Decimal("0.1")
                self.price = base_price + distance_multiplier
            else:
                self.price = base_price

        return super().save(*args, **kwargs)

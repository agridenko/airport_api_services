from rest_framework import serializers

from flights.models import (
    Airport, AirplaneType, Airplane,
    Crew, Route, Flight, Order, Ticket
)


class AirportSerializer(serializers.ModelSerializer):
    """Серіалізатор для моделі Airport"""
    class Meta:
        model = Airport
        fields = [
            "id",
            "name",
            "closest_big_city"
        ]
        read_only_fields = ["id"]


class AirplaneTypeSerializer(serializers.ModelSerializer):
    """Серіалізатор для моделі AirplaneType"""
    class Meta:
        model = AirplaneType
        fields = ["id", "name"]
        read_only_fields = ["id"]


class AirplaneSerializer(serializers.ModelSerializer):
    """Серіалізатор для моделі Airplane (літака)"""
    airplane_type = AirplaneTypeSerializer(read_only=True)
    airplane_type_id = serializers.PrimaryKeyRelatedField(
        queryset=AirplaneType.objects.all(),
        write_only=True,
        source="airplane_type"
    )
    total_seats = serializers.ReadOnlyField()

    class Meta:
        model = Airplane
        fields = [
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type_id",
            "airplane_type",
            "total_seats"
        ]
        read_only_fields = ["id"]


class RouteSerializer(serializers.ModelSerializer):
    """Серіалізатор для моделі Route"""
    source = AirportSerializer(read_only=True)
    source_id = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(),
        write_only=True,
        source="source"
    )

    destination = AirportSerializer(read_only=True)
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(),
        write_only=True,
        source="destination"
    )

    class Meta:
        model = Route
        fields = [
            "id",
            "source_id",
            "source",
            "destination_id",
            "destination",
            "distance"
        ]


class CrewSerializer(serializers.ModelSerializer):
    """Серіалізатор для моделі Crew"""
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]
        read_only_fields = ["id"]


class FlightSerializer(serializers.ModelSerializer):
    """Серіалізатор для моделі Flight"""
    route = RouteSerializer(read_only=True)
    route_id = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.all(),
        write_only=True,
        source="route"
    )
    airplane = AirplaneSerializer(read_only=True)
    airplane_id = serializers.PrimaryKeyRelatedField(
        queryset=Airplane.objects.all(),
        write_only=True,
        source="airplane"
    )
    crew = CrewSerializer(many=True, read_only=True)
    crew_ids = serializers.PrimaryKeyRelatedField(
        queryset=Crew.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="crew"
    )
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = [
            "id",
            "route_id",
            "route",
            "airplane_id",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew_ids",
            "crew",
            "available_seats"
        ]

    def get_available_seats(self, obj):
        """Отримання доступних місць на рейсі"""
        total_seats = obj.airplane.total_seats
        booked_seats = obj.tickets.count()
        return total_seats - booked_seats


class TicketSerializer(serializers.ModelSerializer):
    """Серіалізатор для моделі Ticket"""
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    flight = FlightSerializer(read_only=True)
    flight_id = serializers.PrimaryKeyRelatedField(
        queryset=Flight.objects.all(),
        write_only=True,
        source="flight"
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "flight",
            "flight_id",
            "price"
        ]
        read_only_fields = ["id", "price"]

    def validate(self, data):
        """Перевірка наявності місця на рейсі"""
        flight = data.get("flight")
        row = data.get("row")
        seat = data.get("seat")

        if Ticket.objects.filter(
                flight=flight, row=row, seat=seat
        ).exists():
            raise serializers.ValidationError(
                f"Місце {row}-{seat} вже зайняте на цьому рейсі"
            )

        # Перевірка наявності місця на рейсі
        if row > flight.airplane.rows:
            raise serializers.ValidationError(
                f"Ряд {row} не існує на самоліті"
            )
        if seat > flight.airplane.seats_in_row:
            raise serializers.ValidationError(
                f"Місце {seat} не існує на самоліті"
            )

        return data


class OrderSerializer(serializers.ModelSerializer):
    """Серіалізатор для моделі Order"""
    tickets = TicketSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    total_cost = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "tickets",
            "total_cost",
            "created_at"
        ]

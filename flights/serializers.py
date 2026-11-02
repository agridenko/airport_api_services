from django.utils import timezone
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

    def validate(self, data):
        source = data.get("source")
        destination = data.get("destination")

        if source == destination:
            raise serializers.ValidationError(
                "Початковий та кінцевий аеропорти не можуть бути однаковими"
            )

        if data.get("distance") is None and data["distance"] <= 0:
            raise serializers.ValidationError(
                "Відстань не може бути від'ємною або дорівнювати нулю"
            )

        return data


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
        write_only=True
    )
    airplane = AirplaneSerializer(read_only=True)
    airplane_id = serializers.PrimaryKeyRelatedField(
        queryset=Airplane.objects.all(),
        write_only=True
    )
    crew = CrewSerializer(many=True, read_only=True)
    crew_ids = serializers.PrimaryKeyRelatedField(
        queryset=Crew.objects.all(),
        many=True,
        write_only=True,
        required=False
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

    def validate(self, data):
        departure_time = data.get("departure_time")
        arrival_time = data.get("arrival_time")

        if departure_time and departure_time < timezone.now():
            raise serializers.ValidationError(
                "Час відправлення не може бути меншим за поточний час"
            )

        if arrival_time and arrival_time and arrival_time <= departure_time:
            raise serializers.ValidationError(
                "Час прибуття не може бути "
                "меншим або дорівнювати часу відправлення"
            )

        return data

    def get_available_seats(self, obj):
        """Отримання доступних місць на рейсі"""
        booked_seats = getattr(obj, "booked_seats_count", None)

        if booked_seats is None:
            booked_seats = obj.tickets.count()

        return obj.airplane.total_seats - booked_seats

    def create(self, validated_data):
        crew_data = validated_data.pop("crew_ids", [])
        validated_data["route"] = validated_data.pop("route_id")
        validated_data["airplane"] = validated_data.pop("airplane_id")

        flight = Flight.objects.create(**validated_data)
        flight.crew.set(crew_data)

        return flight

    def update(self, instance, validated_data):
        if "route_id" in validated_data:
            instance.route = validated_data.pop("route_id")
        if "airplane_id" in validated_data:
            instance.airplane = validated_data.pop("airplane_id")
        if "crew_ids" in validated_data:
            instance.crew.set(validated_data.pop("crew_ids"))

        return super().update(instance, validated_data)


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

        if row < 1:
            raise serializers.ValidationError(
                "Ряд має бути більшим або рівним 1."
            )

        if seat < 1:
            raise serializers.ValidationError(
                "Місце має бути більшим або рівним 1."
            )

        if row > flight.airplane.rows:
            raise serializers.ValidationError(
                f"Ряд {row} не існує на літаку."
            )

        if seat > flight.airplane.seats_in_row:
            raise serializers.ValidationError(
                f"Місце {seat} не існує на літаку."
            )

        if Ticket.objects.filter(
                flight=flight, row=row, seat=seat
        ).exists():
            raise serializers.ValidationError(
                f"Місце {row}-{seat} вже зайняте на цьому рейсі"
            )

        return data

    def create(self, validated_data):
        if "flight_id" in validated_data:
            validated_data["flight"] = validated_data.pop("flight_id")
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    """Серіалізатор для моделі Order"""
    tickets = TicketSerializer(many=True, read_only=True)
    user = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "tickets",
            "total_cost",
            "created_at"
        ]

    def get_user(self, obj):
        return (f"{obj.user.first_name} {obj.user.last_name} "
                f"({obj.user.email})").strip() or obj.user.email

    def get_total_cost(self, obj):
        return obj.total_cost

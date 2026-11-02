from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models import Count, F, Sum

from flights.models import (
    Airport, AirplaneType, Airplane,
    Crew, Route, Flight, Order, Ticket
)
from flights.serializers import (
    AirportSerializer, AirplaneTypeSerializer, AirplaneSerializer,
    CrewSerializer, RouteSerializer, FlightSerializer, OrderSerializer,
    TicketSerializer
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["closest_big_city"]
    search_fields = ["name", "closest_big_city"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="closest_big_city",
                description="Фільтрувати аеропорт за найближчим містом",
                required=False,
                type=str
            ),
            OpenApiParameter(
                name="search",
                description="Фільтрувати аеропорт за назвою",
                required=False,
                type=str
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().select_related("airplane_type")
    serializer_class = AirplaneSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["airplane_type"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="airplane_type",
                description="Фільтрувати літак за типом по його id",
                required=False,
                type=int
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=["get"])
    def seats_availability(self, request, pk=None):
        """Повертає кількість доступних місць на літаку."""
        airplane = self.get_object()
        return Response({
            "total_seats": airplane.total_seats,
            "rows": airplane.rows,
            "seats_in_row": airplane.seats_in_row,
        })


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related()
    serializer_class = RouteSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["source", "destination"]

    def get_queryset(self):
        return Route.objects.select_related("source", "destination")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="source",
                description="Фільтрувати маршрут за початковою точкою",
                required=False,
                type=str
            ),
            OpenApiParameter(
                name="destination",
                description="Фільтрувати маршрут за кінцевою точкою",
                required=False,
                type=str
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def from_airport(self, request):
        """Повертає всі маршрути аеропорту."""
        airport_id = request.query_params.get("airport_id")
        if airport_id:
            routes = Route.objects.filter(source_id=airport_id)
            serializer = RouteSerializer(routes, many=True)
            return Response(serializer.data)

        return Response(
            {"error": "airport_id parameter is required"},
            status=status.HTTP_400_BAD_REQUEST
        )


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.select_related(
            "route__source",
            "route__destination",
            "airplane__airplane_type"
        )
        .prefetch_related("crew")
        .annotate(booked_seats_count=Count("tickets"))
    )

    serializer_class = FlightSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["route", "airplane", "departure_time"]
    ordering_fields = ["departure_time", "arrival_time"]
    ordering = ["departure_time"]
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="route",
                description="Фільтрувати рейс за маршрутом по id",
                required=False,
                type=int
            ),
            OpenApiParameter(
                name="airplane",
                description="Фільтрувати рейс за літаком по id",
                required=False,
                type=int
            ),
            OpenApiParameter(
                name="departure_time",
                description="Фільтрувати рейс за часом відправлення (приклад: 2026-11-05T16:00:00Z)",
                required=False,
                type=str
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=["get"])
    def available_seats(self, request, pk=None):
        """Отримати кількість доступних місць на рейсі"""
        flight = self.get_object()
        booked_seats = set(
            (t.row, t.seat) for t in flight.tickets.all()
        )

        available = []
        for row in range(1, flight.airplane.rows + 1):
            for seat in range(1, flight.airplane.seats_in_row + 1):
                if (row, seat) not in booked_seats:
                    available.append({"row": row, "seat": seat})

        return Response({
            "flight_id": flight.id,
            "total_available": len(available),
            "seats": available[:50] # Показуємо перші 50 доступних місць для продуктивності
        })

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """Отримати майбутні рейси"""
        flights = self.get_queryset().filter(departure_time__gte=timezone.now())
        serializer = self.get_serializer(flights, many=True)
        return Response(serializer.data)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    search_fields = ["first_name", "last_name"]
    filter_backends = [filters.SearchFilter]
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="search",
                description="Пошук за ім'ям або прізвищем",
                required=False,
                type=str
            )
        ]
    )
    def list(self, request):
        return super().list(request)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()


class OrderViewSet(viewsets.ModelViewSet):
    queryset = (
        Order.objects.select_related("user")
        .prefetch_related(
            "tickets__flight__route__source",
            "tickets__flight__route__destination",
            "tickets__flight__airplane__airplane_type",
            "tickets__flight__crew"
        ).annotate(total_order_cost=Sum("tickets__price"))
    )

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Створити замовлення для поточного користувача"""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Користувач бачить лише свої замовлення"""
        queryset = self.queryset
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_ticket(self, request, pk=None):
        """Додати квиток до замовлення"""
        order = self.get_object()

        data = request.data.copy()
        data['order'] = order.id

        serializer = TicketSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        serializer.save(order=order)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Користувач бачить тільки свої квитки"""
        queryset = (
            Ticket.objects.select_related(
                "order",
                "flight",
                "flight__route",
                "flight__route__source",
                "flight__route__destination",
                "flight__airplane",
                "flight__airplane__airplane_type",
            )
            .prefetch_related("flight__crew")
        )

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(order__user=self.request.user)

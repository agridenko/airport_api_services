from django.urls import path, include
from rest_framework import routers

from flights.views import (AirportViewSet,
                           AirplaneTypeViewSet,
                           AirplaneViewSet,
                           FlightViewSet,
                           CrewViewSet,
                           OrderViewSet,
                           TicketViewSet,
                           RouteViewSet)

app_name = "flights"

router = routers.DefaultRouter()
router.register("airports", AirportViewSet, basename="airport")
router.register("airplane-types", AirplaneTypeViewSet, basename="airplane-type")
router.register("airplanes", AirplaneViewSet, basename="airplane")
router.register("routes", RouteViewSet, basename="route")
router.register("flights", FlightViewSet, basename="flight")
router.register("crews", CrewViewSet, basename="crew")
router.register("orders", OrderViewSet, basename="order")
router.register("tickets", TicketViewSet, basename="ticket")

urlpatterns = [
    path('', include(router.urls)),
]
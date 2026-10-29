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
router.register("airports", AirportViewSet)
router.register("airplane-types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)
router.register("crews", CrewViewSet)
router.register("orders", OrderViewSet)
router.register("tickets", TicketViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
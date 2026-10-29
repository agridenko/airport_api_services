from django.contrib import admin

from flights.models import (Airport,
                            Flight,
                            AirplaneType,
                            Airplane,
                            Crew,
                            Route,
                            Order,
                            Ticket)


admin.site.register(AirplaneType)
admin.site.register(Crew)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "closest_big_city"]
    ordering = ["id"]


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ["id", "route", "airplane", "departure_time", "arrival_time"]
    ordering = ["departure_time"]


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "rows", "seats_in_row", "airplane_type", "total_seats"]


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ["id", "source", "destination"]
    ordering = ["id"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "total_cost", "created_at"]
    readonly_fields = [
        "id",
        "total_cost",
        "created_at"
    ]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["id", "flight", "row", "seat", "price"]
    readonly_fields = ["id", "price"]

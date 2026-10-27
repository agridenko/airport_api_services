from django.contrib import admin

from flights.models import (Airport,
                            Flight,
                            AirplaneType,
                            Airplane,
                            Crew,
                            Route,
                            Order,
                            Ticket)


admin.site.register(Airport)
admin.site.register(Flight)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Crew)
admin.site.register(Route)
admin.site.register(Order)
admin.site.register(Ticket)

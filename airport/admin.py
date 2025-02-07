from django.contrib import admin

from airport.models import (
    AirplaneType,
    Airplane,
    Flight,
    Route,
    Order,
    Airport,
    Crew
)

admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Flight)
admin.site.register(Route)
admin.site.register(Order)
admin.site.register(Airport)
admin.site.register(Crew)

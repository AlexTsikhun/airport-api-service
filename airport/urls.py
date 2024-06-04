from rest_framework import routers

from airport.views import (
    AirplaneTypeViewSet,
    AirportViewSet,
    CrewViewSet,
    OrderViewSet,
    AirplaneViewSet,
    RouteViewSet,
    FlightViewSet,
    TicketViewSet
)

app_name = "airport"

router = routers.DefaultRouter()
router.register("airplane_type", AirplaneTypeViewSet)
router.register("airport", AirportViewSet)
router.register("crew", CrewViewSet)
router.register("order", OrderViewSet)
router.register("airplane", AirplaneViewSet)
router.register("route", RouteViewSet)
router.register("flight", FlightViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airports", AirportViewSet)
router.register("crews", CrewViewSet)
router.register("orders", OrderViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)
router.register("tickets", TicketViewSet)


urlpatterns = router.urls


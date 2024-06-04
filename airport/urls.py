from rest_framework import routers

from airport.views import (
    AirplaneTypeViewSet,
    AirportViewSet,
    CrewViewSet,
    OrderViewSet,
    AirplaneViewSet,
    RouteViewSet,
    FlightViewSet
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


urlpatterns = router.urls


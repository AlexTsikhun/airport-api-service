from rest_framework import routers

from airport.views import (
    AirplaneTypeViewSet,
    AirportViewSet,
    CrewViewSet,
    OrderViewSet,
    AirplaneViewSet
)

app_name = "airport"

router = routers.DefaultRouter()
router.register("airplane_type", AirplaneTypeViewSet)
router.register("airport", AirportViewSet)
router.register("crew", CrewViewSet)
router.register("order", OrderViewSet)
router.register("airplane", AirplaneViewSet)


urlpatterns = router.urls


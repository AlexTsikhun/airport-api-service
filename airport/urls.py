from rest_framework import routers

from airport.views import (
    AirplaneTypeViewSet,
    AirportViewSet,
    CrewViewSet
)

app_name = "airport"

router = routers.DefaultRouter()
router.register("airplane_type", AirplaneTypeViewSet)
router.register("airport", AirportViewSet)
router.register("crew", CrewViewSet)

urlpatterns = router.urls


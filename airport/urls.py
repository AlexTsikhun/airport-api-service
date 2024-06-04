from rest_framework import routers

from airport.views import (
    AirplaneTypeViewSet,
    AirportViewSet
)

app_name = "airport"

router = routers.DefaultRouter()
router.register("airplane_type", AirplaneTypeViewSet)
router.register("airport", AirportViewSet)

urlpatterns = router.urls


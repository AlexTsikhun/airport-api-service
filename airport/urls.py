from rest_framework import routers

from airport.views import (
    AirplaneTypeViewSet
)

app_name = "airport"

router = routers.DefaultRouter()
router.register("airplane_type", AirplaneTypeViewSet)

urlpatterns = router.urls


from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from airport.models import (
    AirplaneType
)
from airport.serializers import (
    AirplaneTypeSerializer
)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer

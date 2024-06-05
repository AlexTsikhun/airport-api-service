from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from airport.models import (
    AirplaneType,
    Airport,
    Crew,
    Order,
    Airplane,
    Route,
    Flight,
    Ticket
)
from airport.serializers import (
    AirplaneTypeSerializer,
    AirportSerializer,
    CrewSerializer,
    OrderSerializer,
    AirplaneSerializer,
    RouteSerializer,
    FlightSerializer,
    TicketSerializer,
    # AirplaneListSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    # AirplaneDetailSerializer
)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer


    def get_serializer_class(self):
        # if self.action == "list":
        #     return AirplaneListSerializer
        #
        # if self.action == "retrieve":
        #     return AirplaneDetailSerializer

        return AirplaneSerializer


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class FlightViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer


class TicketViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer



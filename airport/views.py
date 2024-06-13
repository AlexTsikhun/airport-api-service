from datetime import datetime

from django.db.models import Count
from django.db.models import F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from airport.models import (
    AirplaneType,
    Airport,
    Crew,
    Order,
    Airplane,
    Route,
    Flight,
    Ticket,
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
    RouteListSerializer,
    RouteDetailSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    TicketListSerializer,
    TicketDetailSerializer,
    AirplaneListSerializer,
    OrderListSerializer,
    AirplaneImageSerializer,
    AirplaneDetailSerializer,
)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirportViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class CrewViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class OrderPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class OrderViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route", "tickets__flight__airplane"
    )
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = OrderPagination

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Airplane.objects.select_related()
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer

        if self.action == "retrieve":
            return AirplaneDetailSerializer

        if self.action == "upload_image":
            return AirplaneImageSerializer

        return AirplaneSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific movie"""
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.select_related()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


class FlightViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Flight.objects.select_related()
    serializer_class = FlightSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in "list":
            queryset = queryset.annotate(
                tickets_available=(
                    F("airplane__rows") * F("airplane__seats_in_row")
                    - Count("tickets")
                )
            )

        departure_time = self.request.query_params.get("departure_time")
        arrival_time = self.request.query_params.get("arrival_time")
        airplane_name = self.request.query_params.get("airplane")

        if departure_time:
            departure_time = datetime.strptime(
                departure_time, "%Y-%m-%d"
            ).date()
            queryset = queryset.filter(departure_time__date=departure_time)

        if arrival_time:
            arrival_time = datetime.strptime(arrival_time, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_time__date=arrival_time)

        if airplane_name:
            queryset = queryset.filter(airplane__name__icontains=airplane_name)

        return queryset.order_by("id")

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "departure_time",
                type={"type": "date"},
                description="Filter by departure time "
                "(ex. ?departure_time=2024-06-09)",
            ),
            OpenApiParameter(
                "arrival_time",
                type={"type": "date"},
                description="Filter by arrival time "
                "(ex. ?arrival_time=2024-06-25)",
            ),
            OpenApiParameter(
                "airplane",
                type=OpenApiTypes.STR,
                description="Filter by airplane name "
                "(ex. ?airplane=Boeing 737)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of all flights"""
        return super().list(request, *args, **kwargs)


class TicketViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer

        if self.action == "retrieve":
            return TicketDetailSerializer

        return TicketSerializer

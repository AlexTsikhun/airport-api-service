from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ValidationError

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


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:  # don't need detail page, simple model no need
        model = AirplaneType
        fields = ("id", "name",)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city",)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name",)


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type",)


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(
            many=False, read_only=True, slug_field="name"
    )

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type",)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance",)


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance",)


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer(
        many=False, read_only=True,  # 'Airport' object is not iterable if many=True

    )
    destination = AirportSerializer(
        many=False, read_only=True,
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance",)


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time")


class FlightListSerializer(FlightSerializer):
    # source and dest (__str__)
    route_info = serializers.CharField(source="route", read_only=True)
    airplane_name = serializers.CharField(source="airplane.name", read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route_info", "airplane_name", "departure_time", "arrival_time")


class FlightDetailSerializer(FlightSerializer):
    route = RouteListSerializer(many=False, read_only=True)
    airplane = AirplaneSerializer(many=False, read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time")


class TicketSerializer(serializers.ModelSerializer):
################################## ERROR WITHOUT error_to_raise

    def validate(self,
                 attrs):
        data = super(TicketSerializer,
                     self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,  # seats_in_row
            ValidationError
        )
        return data
#################################################
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")  # no need order field


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True,
                               read_only=False,
                               allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets",)

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class TicketListSerializer(TicketSerializer):
    flight_info = serializers.CharField(source="flight", read_only=True)
    order = OrderSerializer(many=False, read_only=True)
################################## NO ERROR WITHOUT error_to_raise
    def validate(self,
                 attrs):
        data = super(TicketSerializer,
                     self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,  # seats_in_row
        )
        return data
#########################################
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight_info", "order")


class TicketDetailSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)
    order = OrderSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")

from django.db.models import F, Count
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import (
    Flight,
    Route,
    Airport,
    Airplane,
    AirplaneType
)
from airport.serializers import FlightListSerializer

FLIGHT_URL = reverse("airport:flight-list")


def sample_flight(**params):
    airport = Airport.objects.create(
        name="Freedom", closest_big_city="Lviv"
    )
    route = Route.objects.create(
        source=airport,
        destination=airport,
        distance=50
    )

    airplane_type = AirplaneType.objects.create(name="Big")
    airplane = Airplane.objects.create(
        name="ANN",
        rows=10,
        seats_in_row=10,
        airplane_type=airplane_type
    )

    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": "2024-06-09",
        "arrival_time": "2024-06-25",
    }
    defaults.update(params)

    return Flight.objects.create(**defaults)


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)





class AuthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_flights(self):
        sample_flight()
        sample_flight()

        res = self.client.get(FLIGHT_URL)

        # this is my queryset
        flights = Flight.objects.annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        ).order_by("id")
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_flight_by_departure_time(self):
        airplane_type = AirplaneType.objects.create(name="Small")
        airplane = Airplane.objects.create(
            name="Boeing",
            rows=10,
            seats_in_row=10,
            airplane_type=airplane_type
        )

        flight1 = sample_flight(airplane=airplane)
        flight2 = sample_flight(airplane=airplane, departure_time="2024-06-10")
        flight3 = sample_flight()

        flights = Flight.objects.annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        ).order_by("id").filter(departure_time=flight1.departure_time)

        res = self.client.get(
            FLIGHT_URL, {"departure_time": f"{flight1.departure_time}"}
        )

        serializer1 = FlightListSerializer(flights, many=True)

        self.assertEqual(serializer1.data, res.data)

    def test_filter_flight_by_arrival_time(self):
        airplane_type = AirplaneType.objects.create(name="Small")
        airplane = Airplane.objects.create(
            name="Boeing",
            rows=10,
            seats_in_row=10,
            airplane_type=airplane_type
        )

        flight1 = sample_flight(airplane=airplane, arrival_time="2024-06-25")
        flight2 = sample_flight(airplane=airplane)
        flight3 = sample_flight()

        flights = Flight.objects.annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        ).order_by("id").filter(arrival_time="2024-06-25")

        res = self.client.get(
            FLIGHT_URL, {"arrival_time": "2024-06-25"}
        )

        serializer1 = FlightListSerializer(flights, many=True)

        self.assertEqual(serializer1.data, res.data)

    def test_filter_flights_by_airplane_name(self):
        airplane_type = AirplaneType.objects.create(name="Small")
        airplane = Airplane.objects.create(
            name="Boeing 737",
            rows=10,
            seats_in_row=10,
            airplane_type=airplane_type
        )

        flight1 = sample_flight(airplane=airplane, arrival_time="2024-06-25")
        flight2 = sample_flight(airplane=airplane)
        flight3 = sample_flight()

        flights = Flight.objects.annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        ).order_by("id").filter(airplane__name__icontains="Boeing")

        res = self.client.get(FLIGHT_URL, {"airplane": "Boeing"})

        serializer1 = FlightListSerializer(flights, many=True)

        self.assertEqual(serializer1.data, res.data)

#     def test_retrieve_flight_detail(self):
#         flight = sample_flight()
#         flight.genres.add(Genre.objects.create(name="Genre"))
#         flight.actors.add(
#             Actor.objects.create(first_name="Actor", last_name="Last")
#         )
#
#         url = detail_url(flight.id)
#         res = self.client.get(url)
#
#         serializer = FlightDetailSerializer(flight)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, serializer.data)
#
#     def test_create_flight_forbidden(self):
#         payload = {
#             "title": "Flight",
#             "description": "Description",
#             "duration": 90,
#         }
#         res = self.client.post(MOVIE_URL, payload)
#
#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

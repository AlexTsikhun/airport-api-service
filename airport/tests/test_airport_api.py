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


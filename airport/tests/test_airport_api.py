import os
import tempfile
from datetime import datetime

from PIL import Image
from django.contrib.auth import get_user_model
from django.db.models import (
    F,
    Count
)
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
from airport.serializers import (
    FlightListSerializer,
    FlightDetailSerializer
)

FLIGHT_URL = reverse("airport:flight-list")
AIRPLANE_URL = reverse("airport:airplane-list")


def sample_airport(**params):
    defaults = {
        "name": "Freedom",
        "closest_big_city": "Lviv"
    }
    return Airport.objects.create(**defaults)


def sample_route(**params):
    airport = sample_airport()
    defaults = {
        "source": airport,
        "destination": airport,
        "distance": 50
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_airplane_type(**params):
    defaults = {
        "name": "Big"
    }
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


def sample_airplane():
    airplane_type = sample_airplane_type()
    defaults = {
        "name": "ANN",
        "rows": 10,
        "seats_in_row": 10,
        "airplane_type": airplane_type
    }
    return Airplane.objects.create(**defaults)


def sample_flight(**params):
    route = sample_route()
    airplane = sample_airplane()

    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": "2024-06-09",
        "arrival_time": "2024-06-25",
    }
    defaults.update(params)

    return Flight.objects.create(**defaults)


def detail_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])


def image_upload_url(flight_id):
    """Return URL for recipe image upload"""
    return reverse("airport:airplane-upload-image", args=[flight_id])


def airplane_detail_url(flight_id):
    return reverse("airport:airplane-detail", args=[flight_id])


def convert_full_to_readable_date(datetime_str: str) -> str:
    # convert str to date
    original_date = datetime.strptime(datetime_str,
                                      "%Y-%m-%dT%H:%M:%SZ")

    return original_date.strftime("%Y-%m-%d")


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
        airplane = sample_airplane()

        flight1 = sample_flight(airplane=airplane)
        sample_flight(airplane=airplane, departure_time="2024-06-10")
        sample_flight()

        flights = Flight.objects.annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        ).order_by("id").filter(departure_time=flight1.departure_time)

        res = self.client.get(
            FLIGHT_URL, {"departure_time": "2024-06-09"}  # error with it f"{flight1.departure_time}"}
        )

        serializer1 = FlightListSerializer(flights, many=True)

        self.assertEqual(serializer1.data, res.data)

    def test_filter_flight_by_arrival_time(self):
        airplane = sample_airplane()

        sample_flight(airplane=airplane, arrival_time="2024-06-25")
        sample_flight(airplane=airplane)
        sample_flight()

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
        airplane = sample_airplane()

        sample_flight(airplane=airplane, arrival_time="2024-06-25")
        sample_flight(airplane=airplane)
        sample_flight()

        flights = Flight.objects.annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        ).order_by("id").filter(airplane__name__icontains="Boeing")

        res = self.client.get(FLIGHT_URL, {"airplane": "Boeing"})

        serializer1 = FlightListSerializer(flights, many=True)

        self.assertEqual(serializer1.data, res.data)

    def test_retrieve_flight_detail(self):
        flight = sample_flight()

        url = detail_url(flight.id)
        res = self.client.get(url)
        res.data["arrival_time"] = convert_full_to_readable_date(res.data["arrival_time"])
        res.data["departure_time"] = convert_full_to_readable_date(res.data["departure_time"])

        serializer = FlightDetailSerializer(flight)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_flight_forbidden(self):
        payload = {
            "route": "Some fictitious data for test"
        }
        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_flight(self):
        route = sample_route()
        airplane = sample_airplane()

        payload = {
            "route": 1,
            "airplane": airplane.id,
            "departure_time": "2024-06-09",
            "arrival_time": "2024-06-25",
        }
        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        flight = Flight.objects.get(id=res.data["id"])

        self.assertEqual(flight.route, route)
        self.assertEqual(flight.route, route)
        self.assertIsInstance(flight.airplane, Airplane)
        self.assertIsNotNone(flight.route)


class AirplaneImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "adminn@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.airplane = sample_airplane()

    def tearDown(self):
        self.airplane.image.delete()

    def test_upload_image_to_airplane(self):
        """Test uploading an image to airplane"""
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.airplane.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.airplane.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airplane_list_should_not_work(self):
        url = AIRPLANE_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            # related for "airplane_type": 1,
            sample_airplane_type()

            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "ANN",
                    "rows": 10,
                    "seats_in_row": 10,
                    "airplane_type": 1,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.filter(name="ANN")[0]  # or first()
        self.assertFalse(airplane.image)

    def test_image_url_is_shown_on_airplane_detail(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(airplane_detail_url(self.airplane.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_airplane_list(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(AIRPLANE_URL)

        self.assertIn("image", res.data[0].keys())

    def test_put_airplane_not_allowed(self):
        payload = {
            "route": "Some fictitious data for test"
        }

        airplane = sample_airplane()
        url = detail_url(airplane.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_airplane_not_allowed(self):
        airplane = sample_airplane()
        url = detail_url(airplane.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

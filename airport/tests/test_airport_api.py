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


def sample_airplane(**params):
    airplane_type = AirplaneType.objects.create(name="Big")

    defaults = {
        "name": "ANN",
        "rows": 10,
        "seats_in_row": 10,
        "airplane_type": airplane_type
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


def detail_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])


def image_upload_url(flight_id):
    """Return URL for recipe image upload"""
    return reverse("airport:airplane-upload-image", args=[flight_id])


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
            FLIGHT_URL, {"departure_time": "2024-06-09"}  # error with it f"{flight1.departure_time}"}
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

    def test_retrieve_flight_detail(self):
        flight = sample_flight()

        url = detail_url(flight.id)
        res = self.client.get(url)
        datetime_str = res.data["arrival_time"]
        original_date = datetime.strptime(datetime_str,
                                          '%Y-%m-%dT%H:%M:%SZ')

        res.data["arrival_time"] = original_date.strftime('%Y-%m-%d')

        datetime_str = res.data["departure_time"]
        original_date = datetime.strptime(datetime_str,
                                          '%Y-%m-%dT%H:%M:%SZ')

        res.data["departure_time"] = original_date.strftime('%Y-%m-%d')

        serializer = FlightDetailSerializer(flight)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_flight_forbidden(self):
        payload = {
            "route": "Some fictitious data for test"
        }
        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_flight(self):
        airport = Airport.objects.create(
            name="Freedom",
            closest_big_city="Lviv"
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
        # self.movie_session = sample_movie_session(movie=self.movie)

    def tearDown(self):
        self.airplane.image.delete()

    def test_upload_image_to_airplane(self):
        """Test uploading an image to movie"""
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

    def test_post_image_to_movie_list_should_not_work(self):
        url = AIRPLANE_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            airplane_type = AirplaneType.objects.create(name="Big")

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
    #
    # def test_image_url_is_shown_on_movie_detail(self):
    #     url = image_upload_url(self.movie.id)
    #     with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
    #         img = Image.new("RGB", (10, 10))
    #         img.save(ntf, format="JPEG")
    #         ntf.seek(0)
    #         self.client.post(url, {"image": ntf}, format="multipart")
    #     res = self.client.get(detail_url(self.movie.id))
    #
    #     self.assertIn("image", res.data)
    #
    # def test_image_url_is_shown_on_movie_list(self):
    #     url = image_upload_url(self.movie.id)
    #     with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
    #         img = Image.new("RGB", (10, 10))
    #         img.save(ntf, format="JPEG")
    #         ntf.seek(0)
    #         self.client.post(url, {"image": ntf}, format="multipart")
    #     res = self.client.get(MOVIE_URL)
    #
    #     self.assertIn("image", res.data[0].keys())
    #
    # def test_image_url_is_shown_on_movie_session_detail(self):
    #     url = image_upload_url(self.movie.id)
    #     with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
    #         img = Image.new("RGB", (10, 10))
    #         img.save(ntf, format="JPEG")
    #         ntf.seek(0)
    #         self.client.post(url, {"image": ntf}, format="multipart")
    #     res = self.client.get(MOVIE_SESSION_URL)
    #
    #     self.assertIn("movie_image", res.data[0].keys())
    #
    # def test_put_movie_not_allowed(self):
    #     payload = {
    #         "title": "New movie",
    #         "description": "New description",
    #         "duration": 98,
    #     }
    #
    #     movie = sample_movie()
    #     url = detail_url(movie.id)
    #
    #     res = self.client.put(url, payload)
    #
    #     self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    #
    # def test_delete_movie_not_allowed(self):
    #     movie = sample_movie()
    #     url = detail_url(movie.id)
    #
    #     res = self.client.delete(url)
    #
    #     self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

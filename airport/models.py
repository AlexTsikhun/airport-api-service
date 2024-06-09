from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from rest_framework.serializers import ValidationError

from airport_api_service import settings


class Flight(models.Model):
    route = models.ForeignKey(
        "Route", on_delete=models.CASCADE, related_name="flights"
    )
    airplane = models.ForeignKey(
        "Airplane", on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    # def __str__(self):
    #     return f"{self.route} arrived at {self.departure_time}"


class Route(models.Model):
    source = models.ForeignKey(
        "Airport", on_delete=models.CASCADE, related_name="routes"
    )
    destination = models.ForeignKey(
        "Airport",
        on_delete=models.CASCADE,  # or rename rel_name?
    )
    distance = models.IntegerField()

    # def __str__(self):
    #     # here I don't need source.name, just source
    #     return f"{self.source.name}-{self.destination}"


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        "AirplaneType", on_delete=models.CASCADE, related_name="airplanes"
    )

    # def __str__(self):
    #     return self.name

    # @property
    # def all_places(self):
    #     return self.seats_in_row * self.rows
    #

class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        "Order", on_delete=models.CASCADE, related_name="tickets"
    )

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {airplane_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    # def __str__(self):
    #     return f"Row:{self.row}, Seat:{self.seat}. {self.flight.route}"

    class Meta:
        unique_together = ("row", "seat", "flight")
        ordering = ("row", "seat")


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    )

    # def __str__(self):
    #     return str(self.created_at)


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    # def __str__(self):
    #     return self.name
    #

class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    # def __str__(self):
    #     return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

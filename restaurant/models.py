from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class Menu(models.Model):
    title = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    inventory = models.PositiveIntegerField(validators=[MaxValueValidator(1000000)])

    class Meta:
        ordering = ['id']
        constraints = [models.CheckConstraint(condition=models.Q(price__gt=0), name='capstone_positive_price')]

    def __str__(self):
        return f'{self.title} : {self.price}'

class Booking(models.Model):
    name = models.CharField(max_length=255)
    no_of_guests = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])
    booking_date = models.DateTimeField(db_index=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='capstone_bookings')

    class Meta:
        ordering = ['booking_date', 'id']
        constraints = [
            models.CheckConstraint(condition=models.Q(no_of_guests__gte=1, no_of_guests__lte=20), name='capstone_guest_range'),
            models.UniqueConstraint(fields=['owner', 'booking_date'], name='capstone_unique_owner_time'),
        ]

    def __str__(self):
        return f'{self.name} ({self.no_of_guests}) at {self.booking_date.isoformat()}'

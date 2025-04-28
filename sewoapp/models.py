from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
import hashlib
import hmac


# User model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('partner', 'Partner'),
        ('customer', 'Customer'),
    ]
    
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True)
    id_card_number = models.CharField(max_length=20, blank=True, null=True)
    id_card_photo = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, default=timezone.now)
    
    REQUIRED_FIELDS = ['email', 'role']

class Vehicle(models.Model):
    TYPE_CHOICES = (
        ('car', 'Car'),
        ('motorbike', 'Motorbike'),
    )
    FUEL_CHOICES = (
        ('bbm', 'BBM'),
        ('electric', 'Electric'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=20)
    year = models.IntegerField()
    color = models.CharField(max_length=50, blank=True, null=True)
    daily_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    location = models.CharField(max_length=100)
    mileage = models.IntegerField(blank=True, null=True)
    vehicle_photo = models.URLField(blank=True, null=True)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.license_plate})"


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    pickup_location = models.CharField(max_length=100, blank=True, null=True)
    dropoff_location = models.CharField(max_length=100, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_request = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} - {self.customer.username}"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    payment_gateway_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    payment_date = models.DateTimeField()

    def __str__(self):
        return f"Payment for Booking {self.booking.id}"


class Review(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='review')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer.username}"


class QRCode(models.Model):
    booking = models.OneToOneField('Booking', on_delete=models.CASCADE)
    qr_code_data = models.TextField()
    qr_code_image_url = models.TextField()
    is_scanned = models.BooleanField(default=False)
    scanned_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)  # opsional tambah expired
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_signature(self):
        message = f"{self.booking.id}:{self.booking.customer.id}"
        signature = hmac.new(
            settings.SECRET_KEY.encode(),
            msg=message.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        return signature

    def generate_secure_data(self):
        signature = self.generate_signature()
        return f"{self.booking.id}|{self.booking.customer.id}|{signature}"


class BookingLog(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='logs')
    previous_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='booking_changes')
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for Booking {self.booking.id} changed to {self.new_status}"

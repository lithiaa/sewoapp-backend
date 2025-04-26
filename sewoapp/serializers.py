from rest_framework import serializers
from .models import User, Vehicle, Booking, Payment, Review

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone_number', 'address', 'profile_picture', 'id_card_number', 'id_card_photo', 'is_verified', 'date_joined']

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'owner', 'brand', 'model', 'license_plate', 'year', 'color', 'daily_price', 'description', 'is_available', 'location', 'mileage', 'vehicle_type', 'fuel_type', 'vehicle_photo', 'created_at']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'customer', 'vehicle', 'start_date', 'end_date', 'pickup_location', 'dropoff_location', 'total_price', 'status', 'special_request', 'created_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'payment_gateway_id', 'amount', 'payment_method', 'payment_status', 'payment_date']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'booking', 'customer', 'vehicle', 'rating', 'comment', 'created_at']

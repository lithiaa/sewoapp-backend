from rest_framework import serializers
from .models import User, Vehicle, Booking, Payment, Review, QRCode, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    # Menampilkan role dengan label (misalnya 'Partner' atau 'Customer')
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email', 'password', 'phone_number', 
            'address', 'profile_picture', 'role', 'role_display', 'is_verified', 
            'id_card_number', 'id_card_photo', 'date_joined'
        ]
        read_only_fields = ('id', 'date_joined')


class VehicleSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)  # Biar owner tampil sebagai username, bukan ID

    class Meta:
        model = Vehicle
        fields = [
            'id', 'owner', 'type', 'brand', 'model', 'license_plate', 'year', 'color',
            'daily_price', 'description', 'is_available', 'location', 'mileage',
            'vehicle_photo', 'fuel_type', 'created_at'
        ]
        read_only_fields = ('id', 'owner', 'created_at')
        

class BookingSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    vehicle = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'vehicle', 'start_date', 'end_date',
            'pickup_location', 'dropoff_location', 'total_price', 'status',
            'special_request', 'created_at'
        ]
        read_only_fields = ('id', 'customer', 'created_at', 'status', 'total_price')


class PaymentSerializer(serializers.ModelSerializer):
    booking = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'payment_gateway_id', 'amount',
            'payment_method', 'payment_status', 'payment_date'
        ]
        read_only_fields = ('id', 'booking', 'payment_status', 'payment_date')


class ReviewSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    vehicle = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'booking', 'customer', 'vehicle', 'rating', 'comment', 'created_at'
        ]
        read_only_fields = ('id', 'customer', 'vehicle', 'created_at')


class QRCodeSerializer(serializers.ModelSerializer):
    booking = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = QRCode
        fields = [
            'id', 'booking', 'qr_code_data', 'qr_code_image_url',
            'is_scanned', 'scanned_at', 'expired_at', 'created_at'
        ]
        read_only_fields = ('id', 'booking', 'qr_code_data', 'qr_code_image_url', 'created_at')

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'content', 'timestamp', 'is_read']
        read_only_fields = ['id', 'timestamp', 'sender']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    customer = serializers.SerializerMethodField()
    partner = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'booking', 'customer', 'partner', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_customer(self, obj):
        return UserSerializer(obj.booking.customer).data
    
    def get_partner(self, obj):
        return UserSerializer(obj.booking.vehicle.owner).data
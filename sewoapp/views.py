from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import User, Vehicle, Booking, Payment, Review, QRCode
from .serializers import UserSerializer, VehicleSerializer, BookingSerializer, PaymentSerializer, ReviewSerializer, QRCodeSerializer
import qrcode
from io import BytesIO
import base64
from django.core.files.base import ContentFile
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# UserViewSet
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# VehicleViewSet
class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def perform_create(self, serializer):
        # Simulate a related booking creation or handling QR code generation
        vehicle = serializer.save()

        # Generate QR Code for vehicle (or booking-related task)
        qr_data = f"Vehicle ID: {vehicle.id}, Brand: {vehicle.brand}, Model: {vehicle.model}"
        img = qrcode.make(qr_data)
        buffer = BytesIO()
        img.save(buffer)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        qr_url = f"data:image/png;base64,{img_base64}"
        
        QRCode.objects.create(
            booking=None,  # If related to booking, make sure to connect it.
            qr_code_data=qr_data,
            qr_code_image_url=qr_url
        )

# BookingViewSet
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Handle _changed_by and custom actions before booking creation
        booking = serializer.save(customer=self.request.user)

        # Create QR Code after booking is created
        qr_data = f"Booking ID: {booking.id}, Customer: {booking.customer.username}"
        img = qrcode.make(qr_data)
        buffer = BytesIO()
        img.save(buffer)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        qr_url = f"data:image/png;base64,{img_base64}"

        # Create a QRCode instance after booking
        QRCode.objects.create(
            booking=booking,
            qr_code_data=qr_data,
            qr_code_image_url=qr_url
        )

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        # Custom action to change booking status
        booking = self.get_object()  # Get booking instance
        new_status = request.data.get('status')

        if new_status not in dict(Booking.STATUS_CHOICES).keys():
            return Response({"detail": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)

        if booking.status != new_status:
            booking.status = new_status
            booking._changed_by = request.user  # Set who changed the status
            booking.save()  # Save the status change

            # Trigger the signal for creating the log entry automatically
            return Response(self.get_serializer(booking).data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No status change."}, status=status.HTTP_400_BAD_REQUEST)

# PaymentViewSet
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

# ReviewViewSet
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

# QRCodeViewSet
class QRCodeViewSet(viewsets.ModelViewSet):
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer

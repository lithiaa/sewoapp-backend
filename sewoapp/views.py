from io import BytesIO
import base64

import qrcode
from django.core.files.base import ContentFile
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    Booking,
    Conversation,
    Message,
    Payment,
    QRCode,
    Review,
    User,
    Vehicle,
)
from .serializers import (
    BookingSerializer,
    ConversationSerializer,
    MessageSerializer,
    PaymentSerializer,
    QRCodeSerializer,
    ReviewSerializer,
    UserSerializer,
    VehicleSerializer,
)

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

# Conservation and Message Views

class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Hanya tampilkan conversation yang melibatkan user saat ini
        return Conversation.objects.filter(
            Q(booking__customer=self.request.user) |
            Q(booking__vehicle__owner=self.request.user)
        ).order_by('-updated_at')

class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        conversation = get_object_or_404(Conversation, id=self.kwargs['pk'])
        
        # Verifikasi partisipan conversation
        if self.request.user not in [conversation.booking.customer, conversation.booking.vehicle.owner]:
            raise PermissionDenied("Anda tidak memiliki akses ke percakapan ini")
            
        return conversation

class MessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conversation = get_object_or_404(Conversation, id=self.kwargs['conversation_id'])
        
        # Verifikasi partisipan conversation
        if self.request.user not in [conversation.booking.customer, conversation.booking.vehicle.owner]:
            raise PermissionDenied()
            
        return Message.objects.filter(conversation=conversation).order_by('timestamp')

    def perform_create(self, serializer):
        conversation = get_object_or_404(Conversation, id=self.kwargs['conversation_id'])
        
        # Verifikasi partisipan conversation
        if self.request.user not in [conversation.booking.customer, conversation.booking.vehicle.owner]:
            raise PermissionDenied()
            
        serializer.save(sender=self.request.user, conversation=conversation)

class MessageDetailView(generics.RetrieveAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        message = get_object_or_404(Message, id=self.kwargs['pk'])
        
        # Verifikasi partisipan conversation
        if self.request.user not in [message.conversation.booking.customer, 
                                   message.conversation.booking.vehicle.owner]:
            raise PermissionDenied()
            
        return message

class MarkMessagesAsReadView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        conversation = get_object_or_404(Conversation, id=kwargs['conversation_id'])
        
        # Verifikasi partisipan conversation
        if request.user not in [conversation.booking.customer, conversation.booking.vehicle.owner]:
            raise PermissionDenied()
        
        # Tandai pesan yang belum dibaca sebagai sudah dibaca
        updated = Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        
        return Response({
            'status': 'success',
            'messages_updated': updated
        }, status=status.HTTP_200_OK)

class StartConversationView(generics.CreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, id=request.data.get('booking_id'))
        
        # Verifikasi bahwa user adalah partisipan booking
        if request.user not in [booking.customer, booking.vehicle.owner]:
            raise PermissionDenied("Anda tidak memiliki akses ke booking ini")
        
        # Cek apakah conversation sudah ada
        conversation, created = Conversation.objects.get_or_create(
            booking=booking,
            defaults={'booking': booking}
        )
        
        serializer = self.get_serializer(conversation)
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            headers=headers
        )
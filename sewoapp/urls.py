from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    VehicleViewSet,
    BookingViewSet,
    PaymentViewSet,
    ReviewViewSet,
    QRCodeViewSet,
    ConversationListView,
    ConversationDetailView,
    MessageListView,
    MessageDetailView,
    MarkMessagesAsReadView,
    StartConversationView
)

# Initialize DefaultRouter
router = DefaultRouter()

# Register viewsets with router
router.register(r'users', UserViewSet, basename='user')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'qrcodes', QRCodeViewSet, basename='qrcode')


urlpatterns = [
    # API routes
    path('', include(router.urls)),
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:conversation_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),
    path('conversations/<int:conversation_id>/mark-read/', MarkMessagesAsReadView.as_view(), name='mark-messages-read'),
    path('conversations/start/', StartConversationView.as_view(), name='start-conversation'),
]

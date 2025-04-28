from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, VehicleViewSet, BookingViewSet, PaymentViewSet, ReviewViewSet, QRCodeViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'vehicles', VehicleViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'qrcodes', QRCodeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

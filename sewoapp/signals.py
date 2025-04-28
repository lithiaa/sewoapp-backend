from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Booking, BookingLog
from django.utils import timezone

@receiver(pre_save, sender=Booking)
def save_previous_status(sender, instance, **kwargs):
    """
    Save the current status of the booking before it is updated,
    so we can compare it after saving.
    """
    if instance.pk:
        try:
            existing = Booking.objects.get(pk=instance.pk)
            instance._previous_status = existing.status
        except Booking.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None

@receiver(post_save, sender=Booking)
def create_booking_log(sender, instance, created, **kwargs):
    """
    Create a booking log whenever a booking is created or its status changes.
    """
    changed_by = getattr(instance, '_changed_by', None)
    if not changed_by:
        changed_by = instance.customer  # Default: customer is the changer if not set

    if created:
        BookingLog.objects.create(
            booking=instance,
            previous_status=None,
            new_status=instance.status,
            description="Booking created",
            changed_by=changed_by
        )
    else:
        # Only create log if status actually changed
        if hasattr(instance, '_previous_status') and instance.status != instance._previous_status:
            BookingLog.objects.create(
                booking=instance,
                previous_status=instance._previous_status,
                new_status=instance.status,
                description=f"Status changed from {instance._previous_status} to {instance.status}",
                changed_by=changed_by
            )

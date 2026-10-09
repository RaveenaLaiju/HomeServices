from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import UserProfile, Customer, Provider, Booking_Request, Booking



@receiver(post_save, sender=UserProfile)
def create_profile_related_records(sender, instance, created, raw=False, **kwargs):
    if raw:
        return
    if created and instance.role == 'customer':
        Customer.objects.get_or_create(user_profile=instance)
    elif created and instance.role == 'provider':
        Provider.objects.get_or_create(user_profile=instance)



@receiver(post_save, sender=Booking_Request)
def create_booking_on_accept(sender, instance, created, **kwargs):
    # When a Booking_Request is accepted, create Booking if not exists
    if instance.status and instance.status.lower() == 'accepted':
        Booking.objects.get_or_create(
            booking_request=instance,
            defaults={
                'service_date': timezone.make_aware(timezone.datetime.combine(instance.date, timezone.datetime.min.time())) if instance.date else timezone.now(),
            }
        )

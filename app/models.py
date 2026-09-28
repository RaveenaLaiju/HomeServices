from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('provider', 'Provider'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Service(models.Model):
    service_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='services/')
    price = models.IntegerField()

    def __str__(self):
        return self.service_name

class ServiceSection(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=150)
    

class ServiceSectionItem(models.Model):
    section = models.ForeignKey(ServiceSection, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=150, blank=True, null=True)  # optional subheading
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=150, blank=True, null=True)  # optional subheading
    image = models.ImageField(upload_to='section_items/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)  # for custom ordering

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.section.title} - {self.title or self.description}"


class Provider(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True,related_name="providers")
    location = models.CharField(max_length=100, blank=True)
    experience_years = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='providers/', blank=True, null=True)

    def __str__(self):
        return f"{self.user_profile.user.first_name} {self.user_profile.user.last_name}"

class Customer(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    # other fields like address, gender, etc., optional and blank for now

    def __str__(self):
        return f"{self.user_profile.user.username}"

from datetime import timedelta
from django.utils import timezone
from django.db import models

class Booking_Request(models.Model):
    REQUEST_TYPE = [
        ('normal', 'Normal'),
        ('emergency', 'Emergency'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('rework_pending', 'Rework Requested'),
        ('rework_accepted', 'Rework Accepted'),
        ('rework_completed', 'Rework Completed'),
        ('cancelled', 'Cancelled'),  # ✅ add cancelled here too if not present
    ]

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='requests')
    provider = models.ForeignKey('Provider', on_delete=models.CASCADE, related_name='requests')
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='requests')
    location = models.CharField(max_length=100)
    date = models.DateField()
    type = models.CharField(max_length=20, choices=REQUEST_TYPE, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ Add this new field
    accept_deadline = models.DateTimeField(null=True, blank=True)

    # Rework fields
    is_rework = models.BooleanField(default=False)
    rework_count = models.IntegerField(default=0)
    rework_message = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # ✅ Automatically set accept_deadline only when booking is first created
        if not self.pk and not self.accept_deadline:
            if self.type == 'emergency':
                self.accept_deadline = timezone.now() + timedelta(minutes=30)  # 30 mins for emergency
            else:
                self.accept_deadline = timezone.now() + timedelta(hours=12)   # 12 hrs for normal
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer} - {self.service} ({self.status})"


class Booking(models.Model):
    booking_request = models.OneToOneField(Booking_Request, on_delete=models.CASCADE, related_name='booking')
    booking_date = models.DateTimeField(auto_now_add=True)
    service_date = models.DateTimeField()
    rework_date = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    payment_deadline = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.payment_deadline:
            self.payment_deadline = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking for {self.booking_request.service} ({self.booking_request.status})"



class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failure', 'Failure'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    provider_order_id = models.CharField(max_length=100, blank=True, null=True)
    signature_id = models.CharField(max_length=255, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.id} - {self.payment_status}"

class Review(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, related_name='reviews')
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='reviews')
    provider = models.ForeignKey('Provider', on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='reviews')

    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.customer.user_profile.user.username} - {self.service.service_name} ({self.rating})"

class Enquiry(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
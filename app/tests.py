from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from .models import UserProfile, Provider, Service, Customer, Booking_Request

class BookingRequestAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create customer user
        user = User.objects.create_user(
            username='testcustomer',
            password='testpass123'
        )

        # Creating UserProfile automatically creates Customer
        # through the signal in signals.py
        UserProfile.objects.create(
            user=user,
            role='customer'
        )

        # Authenticate as customer
        self.client.force_authenticate(user=user)

        # Create services
        self.service1 = Service.objects.create(
            service_name='Electrical',
            price=800
        )

        self.service2 = Service.objects.create(
            service_name='Plumbing',
            price=700
        )

        # Create provider user
        provider_user = User.objects.create_user(
            username='testprovider',
            password='testpass123'
        )

        # Creating UserProfile automatically creates Provider
        # through the signal in signals.py
        provider_profile = UserProfile.objects.create(
            user=provider_user,
            role='provider'
        )

        # Get the Provider created automatically by the signal
        self.provider = Provider.objects.get(
            user_profile=provider_profile
        )

        # Set provider details
        self.provider.service = self.service1
        self.provider.location = 'Ernakulam'
        self.provider.experience_years = 4
        self.provider.save()

    def test_invalid_provider_service(self):
        response = self.client.post(
            '/api/booking-requests/',
            {
                'provider': self.provider.id,
                'service': self.service2.id,
                'location': 'Ernakulam',
                'date': '2026-10-20',
                'type': 'normal'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)

    def test_valid_booking_creation(self):
        response = self.client.post(
            '/api/booking-requests/',
            {
                'provider': self.provider.id,
                'service': self.service1.id,
                'location': 'Ernakulam',
                'date': '2026-10-20',
                'type': 'normal'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)

    def test_customer_cannot_access_other_customer_booking(self):
        # Create another customer
        other_user = User.objects.create_user(
            username='othercustomer',
            password='testpass123'
        )

        UserProfile.objects.create(
            user=other_user,
            role='customer'
        )

        # Create a booking for the other customer
        from .models import Customer, Booking_Request

        other_customer = Customer.objects.get(
            user_profile__user=other_user
        )

        booking = Booking_Request.objects.create(
            customer=other_customer,
            provider=self.provider,
            service=self.service1,
            location='Ernakulam',
            date='2026-10-20',
            type='normal'
        )

        # Current logged-in user tries to access it
        response = self.client.get(
            f'/api/booking-requests/{booking.id}/'
        )

        self.assertEqual(response.status_code, 404)

    def test_past_booking_date(self):
        response = self.client.post(
            '/api/booking-requests/',
            {
                'provider': self.provider.id,
                'service': self.service1.id,
                'location': 'Ernakulam',
                'date': '2020-01-01',
                'type': 'normal'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)

    def test_filter_booking_by_status(self):

        user = self.client.handler._force_user

        customer = Customer.objects.get(
            user_profile__user=user
        )

        Booking_Request.objects.create(
            customer=customer,
            provider=self.provider,
            service=self.service1,
            location='Ernakulam',
            date='2026-10-20',
            type='normal',
            status='pending'
        )

        Booking_Request.objects.create(
            customer=customer,
            provider=self.provider,
            service=self.service1,
            location='Kochi',
            date='2026-10-21',
            type='normal',
            status='completed'
        )

        response = self.client.get(
            '/api/booking-requests/?status=pending'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['status'],
            'pending'
        )

    def test_booking_pagination(self):

        user = self.client.handler._force_user

        customer = Customer.objects.get(
            user_profile__user=user
        )

        for i in range(7):
            Booking_Request.objects.create(
                customer=customer,
                provider=self.provider,
                service=self.service1,
                location='Ernakulam',
                date='2026-10-20',
                type='normal',
                status='pending'
            )

        response = self.client.get(
            '/api/booking-requests/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 7)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNotNone(response.data['next'])

    def test_service_list_api(self):
        response = self.client.get('/api/services/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)

    def test_provider_list_api(self):
        response = self.client.get('/api/providers/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)

        provider = response.data['results'][0]

        self.assertEqual(
            provider['service']['id'],
            self.service1.id
        )

    def test_anonymous_user_cannot_create_booking(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            '/api/booking-requests/',
            {
                'provider': self.provider.id,
                'service': self.service1.id,
                'location': 'Ernakulam',
                'date': '2026-10-20',
                'type': 'normal'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_can_view_services(self):
        self.client.force_authenticate(user=None)

        response = self.client.get('/api/services/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)

    def test_anonymous_user_cannot_view_bookings(self):
        self.client.force_authenticate(user=None)

        response = self.client.get('/api/booking-requests/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])

    def test_service_search(self):
        response = self.client.get(
            '/api/services/?search=Electrical'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['service_name'],
            'Electrical'
        )

    def test_provider_search_by_location(self):
        response = self.client.get(
            '/api/providers/?search=Ernakulam'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['location'],
            'Ernakulam'
        )

    def test_booking_search_by_location(self):
        response = self.client.get(
            '/api/booking-requests/?search=Ernakulam'
        )

        self.assertEqual(response.status_code, 200)

        for booking in response.data['results']:
            self.assertEqual(
                booking['location'],
                'Ernakulam'
            )
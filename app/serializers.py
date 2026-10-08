from rest_framework import serializers
from .models import Service, Provider, Booking_Request

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class ProviderSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = Provider
        fields = [
            'id',
            'location',
            'experience_years',
            'photo',
            'user_profile',
            'service',
        ]

class BookingRequestSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(read_only=True)

    provider_details = ProviderSerializer(
        source='provider',
        read_only=True
    )

    service_details = ServiceSerializer(
        source='service',
        read_only=True
    )

    def validate(self, data):
        provider = data.get('provider')
        service = data.get('service')
        booking_date = data.get('date')

        if provider and service:
            if provider.service_id != service.id:
                raise serializers.ValidationError(
                    "The selected provider does not provide the selected service."
                )

        if booking_date:
            from django.utils import timezone

            if booking_date < timezone.localdate():
                raise serializers.ValidationError(
                    "Booking date cannot be in the past."
                )

        return data

    class Meta:
        model = Booking_Request
        fields = [
            'id',
            'customer',
            'provider',
            'provider_details',
            'service',
            'service_details',
            'location',
            'date',
            'type',
            'status',
            'created_at',
            'accept_deadline',
            'is_rework',
            'rework_count',
            'rework_message',
        ]
        read_only_fields = [
            'customer',
            'status',
            'created_at',
            'accept_deadline',
        ]
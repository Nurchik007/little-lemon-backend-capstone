from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers
from .models import Booking, Menu

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'title', 'price', 'inventory']

class BookingSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Booking
        fields = ['id', 'name', 'no_of_guests', 'booking_date', 'owner']
        # Owner is assigned from the request; validate the combined key below.
        validators = []

    def validate_booking_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError('Choose a future date and time (UTC or an explicit offset).')
        return value

    def validate(self, attrs):
        owner = self.instance.owner if self.instance else self.context['request'].user
        date = attrs.get('booking_date', self.instance.booking_date if self.instance else None)
        duplicates = Booking.objects.filter(owner=owner, booking_date=date)
        if self.instance:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError({'booking_date': 'You already have a booking at this time.'})
        return attrs

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, max_length=128, trim_whitespace=False)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'password']
        read_only_fields = ['id']

    def validate(self, attrs):
        user = get_user_model()(username=attrs['username'])
        try:
            password_validation.validate_password(attrs['password'], user)
        except DjangoValidationError as error:
            raise serializers.ValidationError({'password': error.messages})
        return attrs

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

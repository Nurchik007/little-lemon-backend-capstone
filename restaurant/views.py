from django.db import IntegrityError, transaction
from djoser.views import TokenCreateView
from rest_framework import generics, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from .models import Booking, Menu
from .serializers import BookingSerializer, MenuSerializer, RegistrationSerializer

class StaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or bool(request.user and request.user.is_staff)

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [StaffOrReadOnly]

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = Booking.objects.select_related('owner')
        return query.all() if self.request.user.is_staff else query.filter(owner=self.request.user)

    def perform_create(self, serializer):
        self._save(serializer, owner=self.request.user)

    def perform_update(self, serializer):
        self._save(serializer)

    @staticmethod
    def _save(serializer, **kwargs):
        from rest_framework.exceptions import ValidationError
        try:
            with transaction.atomic():
                serializer.save(**kwargs)
        except IntegrityError:
            # The unique index also protects a race between two valid requests.
            raise ValidationError({'booking_date': 'Booking conflicts with an existing record.'})

class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'authentication'

class LoginView(ObtainAuthToken):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'authentication'

# A named DRF token view callable, preserving the scoped authentication throttle.
obtain_auth_token = LoginView.as_view()

class DjoserTokenCreateView(TokenCreateView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'authentication'

class LogoutView(APIView):
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MeView(APIView):
    def get(self, request):
        return Response({'id': request.user.pk, 'username': request.user.username, 'is_staff': request.user.is_staff})

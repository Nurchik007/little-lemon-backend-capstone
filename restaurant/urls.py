from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('menu', views.MenuViewSet, basename='menu')
router.register('bookings', views.BookingViewSet, basename='booking')
urlpatterns = [
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('api-token-auth/', views.obtain_auth_token, name='token'),
    path('token/login/', views.LoginView.as_view()),
    path('token/logout/', views.LogoutView.as_view(), name='logout'),
    path('users/me/', views.MeView.as_view(), name='me'),
    path('', include(router.urls)),
]

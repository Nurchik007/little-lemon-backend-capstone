from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('bookings', views.BookingViewSet, basename='booking')
urlpatterns = [
    path('menu/', views.MenuItemsView.as_view(), name='menu-list'),
    path('menu/<int:pk>/', views.SingleMenuItemView.as_view(), name='menu-detail'),
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('api-token-auth/', views.LoginView.as_view(), name='token'),
    path('token/login/', views.LoginView.as_view()),
    path('token/logout/', views.LogoutView.as_view(), name='logout'),
    path('users/me/', views.MeView.as_view(), name='me'),
    path('', include(router.urls)),
]

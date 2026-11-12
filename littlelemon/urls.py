from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from restaurant import views

router = DefaultRouter()
router.register('tables', views.BookingViewSet, basename='table')
urlpatterns = [
    path('', TemplateView.as_view(template_name='restaurant/index.html'), name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('restaurant.urls')),
    path('restaurant/', include('restaurant.urls')),
    path('restaurant/booking/', include(router.urls)),
    path('api-token-auth/', views.LoginView.as_view()),
    path('api-auth/', include('rest_framework.urls')),
]

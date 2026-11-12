from django.apps import AppConfig

class RestaurantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'restaurant'
    # Separate migration/table namespace from earlier, unrelated course projects.
    label = 'capstone_restaurant'
    verbose_name = 'Little Lemon Capstone'

from decimal import Decimal
from django.core.management.base import BaseCommand
from restaurant.models import Menu

class Command(BaseCommand):
    help = 'Add three demonstration dishes without creating accounts or changing existing dishes.'

    def handle(self, *args, **options):
        for title, price, inventory in [('Greek salad', '12.50', 30), ('Bruschetta', '8.00', 20), ('Lemon dessert', '7.50', 15)]:
            Menu.objects.get_or_create(title=title, defaults={'price': Decimal(price), 'inventory': inventory})
        self.stdout.write(self.style.SUCCESS('Demonstration menu is ready.'))

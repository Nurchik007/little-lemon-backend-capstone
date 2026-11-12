from decimal import Decimal
from django.db import connection
from django.test import TestCase
from restaurant.models import Menu


class MenuTest(TestCase):
    def test_string_representation(self):
        item = Menu.objects.create(title='IceCream', price=Decimal('80.00'), inventory=100)
        self.assertEqual(str(item), 'IceCream : 80.00')

    def test_mysql_persists_decimal_and_inventory(self):
        self.assertEqual(connection.vendor, 'mysql')
        item = Menu.objects.create(title='Soup', price=Decimal('12.50'), inventory=12)
        loaded = Menu.objects.get(pk=item.pk)
        self.assertEqual((loaded.title, loaded.price, loaded.inventory), ('Soup', Decimal('12.50'), 12))



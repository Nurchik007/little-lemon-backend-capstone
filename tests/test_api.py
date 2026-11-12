from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.test import TestCase
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from restaurant.models import Booking, Menu
from restaurant.serializers import MenuSerializer


class MenuTest(TestCase):
    def test_string_representation(self):
        item = Menu.objects.create(title='IceCream', price=Decimal('80.00'), inventory=100)
        self.assertEqual(str(item), 'IceCream : 80.00')

    def test_mysql_persists_decimal_and_inventory(self):
        self.assertEqual(connection.vendor, 'mysql')
        item = Menu.objects.create(title='Soup', price=Decimal('12.50'), inventory=12)
        loaded = Menu.objects.get(pk=item.pk)
        self.assertEqual((loaded.title, loaded.price, loaded.inventory), ('Soup', Decimal('12.50'), 12))


class MenuViewTest(APITestCase):
    def setUp(self):
        cache.clear()
        self.customer = get_user_model().objects.create_user('customer', password='A-test-only-Passphrase-742!')
        self.staff = get_user_model().objects.create_user('staff', password='Another-test-Passphrase-135!', is_staff=True)
        self.menu = Menu.objects.create(title='Greek salad', price=Decimal('12.50'), inventory=30)
        Menu.objects.create(title='Bruschetta', price=Decimal('8.00'), inventory=20)

    def test_getall_matches_serializer(self):
        response = self.client.get('/api/menu/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], MenuSerializer(Menu.objects.all(), many=True).data)
        self.assertEqual(response.data['count'], 2)

    def test_home_serves_html_and_static_asset_link(self):
        response = self.client.get('/')
        self.assertContains(response, 'Good food.')
        self.assertContains(response, '/static/restaurant/site.css')
        self.assertContains(response, '/api/bookings/')

    def test_menu_detail_and_missing_item(self):
        self.assertEqual(self.client.get(f'/api/menu/{self.menu.pk}/').data['price'], '12.50')
        self.assertEqual(self.client.get('/api/menu/999999/').status_code, 404)

    def test_customer_cannot_write_menu(self):
        self.client.force_authenticate(self.customer)
        self.assertEqual(self.client.post('/api/menu/', {'title': 'Steak', 'price': '20.00', 'inventory': 5}).status_code, 403)
        self.assertEqual(self.client.delete(f'/api/menu/{self.menu.pk}/').status_code, 403)

    def test_staff_menu_post_put_delete(self):
        self.client.force_authenticate(self.staff)
        created = self.client.post('/api/menu/', {'title': 'Lemon dessert', 'price': '7.50', 'inventory': 6})
        self.assertEqual(created.status_code, 201)
        url = f"/api/menu/{created.data['id']}/"
        changed = self.client.put(url, {'title': 'Lemon dessert', 'price': '8.25', 'inventory': 8})
        self.assertEqual(changed.status_code, 200)
        self.assertEqual(Menu.objects.get(pk=created.data['id']).price, Decimal('8.25'))
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertFalse(Menu.objects.filter(pk=created.data['id']).exists())

    def test_menu_rejects_invalid_prices_and_stock(self):
        self.client.force_authenticate(self.staff)
        for price, inventory in [('0.00', 1), ('-1.00', 1), ('5.00', -1), ('5.00', 1000001)]:
            with self.subTest(price=price, inventory=inventory):
                self.assertEqual(self.client.post('/api/menu/', {'title': 'Invalid', 'price': price, 'inventory': inventory}).status_code, 400)
        self.assertEqual(Menu.objects.count(), 2)


class AuthenticationAndBookingTest(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user('alice', password='Test-only-Strong-Passphrase-834!')
        self.other = get_user_model().objects.create_user('bob', password='Test-only-Different-Passphrase-425!')
        self.staff = get_user_model().objects.create_user('manager', password='Test-only-Manager-Passphrase-539!', is_staff=True)
        self.future = (timezone.now() + timedelta(days=2)).replace(microsecond=0)

    def payload(self, **extra):
        return {'name': 'Alice', 'no_of_guests': 2, 'booking_date': self.future.isoformat(), **extra}

    def test_registration_hashes_password_and_prevents_privilege_escalation(self):
        password = 'New-test-only-Passphrase-712!'
        response = self.client.post('/api/registration/', {'username': 'newguest', 'password': password, 'is_staff': True, 'is_superuser': True}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertNotIn('password', response.data)
        user = get_user_model().objects.get(username='newguest')
        self.assertTrue(user.check_password(password))
        self.assertNotEqual(user.password, password)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_weak_and_duplicate_registrations_are_rejected(self):
        self.assertEqual(self.client.post('/api/registration/', {'username': 'newguest', 'password': '123'}).status_code, 400)
        self.assertEqual(self.client.post('/api/registration/', {'username': 'alice', 'password': 'Strong-test-only-Passphrase-328!'}).status_code, 400)

    def test_actual_token_login_and_logout_revocation(self):
        response = self.client.post('/api/api-token-auth/', {'username': 'alice', 'password': 'Test-only-Strong-Passphrase-834!'})
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])
        self.assertEqual(self.client.get('/api/users/me/').data['username'], 'alice')
        self.assertEqual(self.client.post('/api/token/logout/').status_code, 204)
        self.assertEqual(self.client.get('/api/bookings/').status_code, 401)

    def test_bad_credentials_and_invalid_tokens(self):
        self.assertEqual(self.client.post('/api-token-auth/', {'username': 'alice', 'password': 'wrong'}).status_code, 400)
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid')
        self.assertEqual(self.client.get('/api/bookings/').status_code, 401)

    def test_bearer_header_for_insomnia(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)
        self.assertEqual(self.client.get('/api/users/me/').data['username'], 'alice')

    def test_anonymous_booking_access_is_denied(self):
        self.assertEqual(self.client.get('/api/bookings/').status_code, 401)
        self.assertEqual(self.client.post('/api/bookings/', self.payload()).status_code, 401)

    def test_booking_full_crud_and_server_assigned_owner(self):
        self.client.force_authenticate(self.user)
        created = self.client.post('/api/bookings/', self.payload(owner='bob'), format='json')
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data['owner'], 'alice')
        url = f"/api/bookings/{created.data['id']}/"
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.get('/api/bookings/').data['count'], 1)
        self.assertEqual(self.client.put(url, self.payload(no_of_guests=4), format='json').status_code, 200)
        self.assertEqual(Booking.objects.get(pk=created.data['id']).no_of_guests, 4)
        self.assertEqual(self.client.patch(url, {'name': 'Alice Smith'}, format='json').status_code, 200)
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_cross_user_booking_list_detail_update_and_delete_are_isolated(self):
        booking = Booking.objects.create(owner=self.other, name='Bob', no_of_guests=2, booking_date=self.future)
        self.client.force_authenticate(self.user)
        url = f'/api/bookings/{booking.pk}/'
        self.assertEqual(self.client.get('/api/bookings/').data['count'], 0)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.patch(url, {'name': 'Hijacked'}).status_code, 404)
        self.assertEqual(self.client.delete(url).status_code, 404)
        self.assertEqual(Booking.objects.get(pk=booking.pk).name, 'Bob')

    def test_staff_can_manage_other_bookings_without_reassigning_owner(self):
        booking = Booking.objects.create(owner=self.other, name='Bob', no_of_guests=2, booking_date=self.future)
        self.client.force_authenticate(self.staff)
        response = self.client.patch(f'/api/bookings/{booking.pk}/', {'no_of_guests': 3, 'owner': 'manager'})
        self.assertEqual(response.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual((booking.no_of_guests, booking.owner_id), (3, self.other.pk))

    def test_invalid_dates_guest_counts_and_duplicate_time_are_rejected(self):
        self.client.force_authenticate(self.user)
        for guests in [0, 21, -1]:
            self.assertEqual(self.client.post('/api/bookings/', self.payload(no_of_guests=guests), format='json').status_code, 400)
        self.assertEqual(self.client.post('/api/bookings/', self.payload(booking_date=(timezone.now()-timedelta(days=1)).isoformat()), format='json').status_code, 400)
        self.assertEqual(self.client.post('/api/bookings/', self.payload(), format='json').status_code, 201)
        self.assertEqual(self.client.post('/api/bookings/', self.payload(), format='json').status_code, 400)
        self.assertEqual(Booking.objects.count(), 1)

    def test_course_compatibility_routes_share_the_same_records(self):
        self.client.force_authenticate(self.user)
        created = self.client.post('/restaurant/booking/tables/', self.payload(), format='json')
        self.assertEqual(created.status_code, 201)
        self.assertEqual(self.client.get('/api/bookings/').data['results'][0]['id'], created.data['id'])
        self.assertEqual(self.client.get('/restaurant/menu/').status_code, 200)

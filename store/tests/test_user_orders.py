from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from store.models import Customer, Order, Product, OrderItem, ShippingAddress
import json

User = get_user_model()

class OrderViewsTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass', email='test@example.com')
        self.customer = Customer.objects.create(user=self.user)
        self.product = Product.objects.create(name='TestProd', price=10.0, category='Cat')

        # Логін користувача для тестів, що потребують авторизації
        self.client.login(username='testuser', password='pass')

        # URL-и (потрібно замінити на свої імена роутів)
        self.cancel_url = reverse('cancel_order')
        self.orders_url = reverse('orders')
        self.place_url = reverse('place_order')

    # Тести cancel_order

    def test_cancel_order_success(self):
        order = Order.objects.create(customer=self.customer, is_canceled=False, is_shipped=False)
        response = self.client.post(self.cancel_url, {'order_id': order.id})
        order.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
        self.assertTrue(order.is_canceled)

    def test_cancel_order_missing_order_id(self):
        response = self.client.post(self.cancel_url, {})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Order ID missing', response.json().get('error', ''))

    def test_cancel_order_already_canceled(self):
        order = Order.objects.create(customer=self.customer, is_canceled=True)
        response = self.client.post(self.cancel_url, {'order_id': order.id})
        self.assertEqual(response.status_code, 400)
        self.assertIn('already canceled', response.json().get('error', ''))

    # Тести user_orders_view

    def test_user_orders_view_with_orders(self):
        Order.objects.create(customer=self.customer)
        Order.objects.create(customer=self.customer)
        response = self.client.get(self.orders_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('orders', response.context)
        self.assertEqual(len(response.context['orders']), 2)

    def test_user_orders_view_no_customer(self):
        # Створимо користувача без Customer
        new_user = User.objects.create_user(username='nouser', password='pass')
        self.client.login(username='nouser', password='pass')
        response = self.client.get(self.orders_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['orders']), 0)

    # Тести place_order

    def test_place_order_logged_in_user(self):
        cart_items = [{'id': self.product.id, 'quantity': 1}]
        session = self.client.session
        session['cart_items'] = cart_items
        session.save()

        data = {
            "full_name": "Test User",
            "email": self.user.email,  # співпадає з email залогіненого
            "phone": "123456789",
            "address": "123 Main St",
            "city": "City",
            "postal_code": "12345",
            "payment_method": "card"
        }

        response = self.client.post(self.place_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        self.assertTrue(Order.objects.filter(customer=self.customer).exists())
        self.assertTrue(ShippingAddress.objects.exists())
        self.assertTrue(OrderItem.objects.exists())

    def test_place_order_guest_user(self):
        self.client.logout()  # Гость, без авторизації
        cart_items = [{'id': self.product.id, 'quantity': 1}]
        session = self.client.session
        session['cart_items'] = cart_items
        session.save()

        data = {
            "full_name": "John Guest",
            "email": "guest@example.com",
            "phone": "987654321",
            "address": "456 Another St",
            "city": "Town",
            "postal_code": "54321",
            "payment_method": "paypal"
        }

        response = self.client.post(self.place_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        self.assertTrue(Order.objects.exists())
        self.assertTrue(ShippingAddress.objects.exists())
        self.assertTrue(OrderItem.objects.exists())

    def test_place_order_empty_cart(self):
        data = {
            "full_name": "No Cart",
            "email": "nocart@example.com",
            "phone": "000000000",
            "address": "Nowhere",
            "city": "None",
            "postal_code": "00000",
            "payment_method": "card"
        }
        response = self.client.post(self.place_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('you cannot use a different email while logged in', response.json().get('error', '').lower())
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from store.models import Order, Customer
from datetime import date
import json

User = get_user_model()


class ManageOrdersViewTests(TestCase):

    def setUp(self):
        # Створюємо користувача зі staff-правами
        self.staff_user = User.objects.create_user(username='admin', password='pass')
        self.staff_user.is_staff = True
        self.staff_user.save()

        self.client = Client()
        self.client.login(username='admin', password='pass')

        # Створюємо замовлення для тестів
        self.customer = Customer.objects.create(user=self.staff_user)
        self.order = Order.objects.create(
            customer=self.customer,
            order_date=date.today(),
            is_approved=False,
            is_canceled=False
        )

    def test_get_orders_page(self):
        response = self.client.get(reverse('manage_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('orders', response.context)

    def test_filter_by_order_id(self):
        response = self.client.get(reverse('manage_orders'), {'order_id': self.order.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['orders']), 1)

    def test_approve_order_success(self):
        response = self.client.post(
            reverse('manage_orders'),
            {'action': 'approve', 'order_id': self.order.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.order.refresh_from_db()
        self.assertTrue(self.order.is_approved)

    def test_approve_order_already_approved(self):
        self.order.is_approved = True
        self.order.save()
        response = self.client.post(
            reverse('manage_orders'),
            {'action': 'approve', 'order_id': self.order.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Order already approved')

    def test_cancel_order_success(self):
        response = self.client.post(
            reverse('manage_orders'),
            {'action': 'cancel', 'order_id': self.order.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.order.refresh_from_db()
        self.assertTrue(self.order.is_canceled)
        self.assertFalse(self.order.is_approved)

    def test_cancel_order_already_canceled(self):
        self.order.is_canceled = True
        self.order.save()
        response = self.client.post(
            reverse('manage_orders'),
            {'action': 'cancel', 'order_id': self.order.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Order already canceled')

    def test_add_tracking_success(self):
        response = self.client.post(
            reverse('manage_orders'),
            {'action': 'add_tracking', 'order_id': self.order.id, 'tracking_code': 'TRACK123'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.order.refresh_from_db()
        self.assertEqual(self.order.tracking_code, 'TRACK123')
        self.assertTrue(self.order.is_shipped)
        self.assertIsNotNone(self.order.shipped_date)
        self.assertIsNotNone(self.order.estimated_shipping_date)

    def test_add_tracking_empty_code(self):
        response = self.client.post(
            reverse('manage_orders'),
            {'action': 'add_tracking', 'order_id': self.order.id, 'tracking_code': ''},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Tracking code cannot be empty')

    def test_add_tracking_to_canceled_order(self):
        self.order.is_canceled = True
        self.order.save()
        response = self.client.post(
            reverse('manage_orders'),
            {'action': 'add_tracking', 'order_id': self.order.id, 'tracking_code': 'TRACK123'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Cannot add tracking to canceled order')

    def test_invalid_action(self):
        response = self.client.post(
            reverse('manage_orders'),
            {'action': 'unknown', 'order_id': self.order.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Invalid action')

    def test_non_staff_cannot_access(self):
        # Вийдемо з сесії staff
        self.client.logout()
        user = User.objects.create_user(username='regular', password='pass')
        self.client.login(username='regular', password='pass')

        response = self.client.get(reverse('manage_orders'))
        self.assertNotEqual(response.status_code, 200)  # повинен бути редірект чи 403
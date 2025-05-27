from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthViewsTests(TestCase):

    def test_register_get(self):
        # GET запит має повернути 200 і форму в контексті
        response = self.client.get(reverse('registration'))  # або '/register/', як у тебе
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_register_post_valid(self):
        # POST запит з валідними даними має створити користувача і залогінити
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '1234567890',
            'password1': 'StrongPassw0rd!',
            'password2': 'StrongPassw0rd!',
        }
        response = self.client.post(reverse('registration'), data)
        # Перевірка редіректу після успішної реєстрації
        self.assertRedirects(response, '/')
        # Перевірка, що користувач створений
        self.assertTrue(User.objects.filter(username='testuser').exists())
        # Перевірка, що користувач залогінений
        user = User.objects.get(username='testuser')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_register_post_invalid(self):
        # POST з некоректними даними (наприклад, паролі не співпадають)
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': '',  # відсутній first_name
            'last_name': '',  # відсутній last_name
            'phone': '',  # відсутній phone
            'password1': 'password123',
            'password2': 'password321',  # різні паролі
        }
        response = self.client.post(reverse('registration'), data)
        # Повинно повернути сторінку з помилками (код 200, але без редіректу)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password2', "The two password fields didn’t match.")
        # Користувач НЕ створений
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_login_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_login_post_valid(self):
        # Спочатку створимо користувача
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        data = {
            'email': 'test@example.com',  # враховуючи що у тебе EmailLoginForm
            'password': 'testpass123',
        }
        response = self.client.post(reverse('login'), data)
        self.assertRedirects(response, '/')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_login_post_invalid(self):
        data = {
            'email': 'wrong@example.com',
            'password': 'wrongpass',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertFalse('_auth_user_id' in self.client.session)
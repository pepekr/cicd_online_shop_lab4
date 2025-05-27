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
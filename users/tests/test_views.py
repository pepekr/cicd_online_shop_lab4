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
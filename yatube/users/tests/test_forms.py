from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


User = get_user_model()


class UsersFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_new_user(self):
        """Проверка создания нового юзера"""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Stas',
            'last_name': 'Basov',
            'username': 'stasik',
            'email': 'stasik@mail.ru',
            'password1': 'test_pass',
            'password2': 'test_pass',
        }
        self.guest_client.post(reverse('users:signup'), data=form_data)
        self.assertEqual(User.objects.count(), users_count + 1)

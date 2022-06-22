from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


User = get_user_model()


class UserURLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.page_names_with_templates = (
            ('users:login', 'users/login.html'),
            ('users:password_reset', 'users/password_reset.html'),
            ('users:password_reset_done', 'users/password_reset_done.html'),
            ('users:password_reset_complete', (
                'users/password_reset_complete.html')),
            ('users:signup', 'users/signup.html'),
            ('users:password_change', 'users/password_change.html'),
            ('users:password_change_done', 'users/password_change_done.html'),
            ('users:logout', 'users/logged_out.html'),
        )

    def test_urls_equal_reverse_urls(self):
        """Проверка соответствия url реверсам."""
        page_names_with_urls = (
            ('users:login', '/auth/login/'),
            ('users:password_reset', '/auth/password_reset/'),
            ('users:password_reset_done', '/auth/password_reset/done/'),
            ('users:password_reset_complete', '/auth/reset/done/'),
            ('users:password_change', '/auth/password_change/'),
            ('users:password_change_done', '/auth/password_change/done/'),
            ('users:signup', '/auth/signup/'),
            ('users:logout', '/auth/logout/'),
        )
        for name, url, in page_names_with_urls:
            with self.subTest(url=url):
                self.assertEqual(reverse(name), url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for name, template, in self.page_names_with_templates:
            with self.subTest(page_name=name):
                response = self.authorized_client.get(reverse(name))
                self.assertTemplateUsed(response, template)

    def test_urls_exists_at_desired_location(self):
        """Cтраницы доступные любому пользователю."""
        for name, _, in self.page_names_with_templates:
            with self.subTest(page_name=name):
                templates = ['users:password_change',
                             'users:password_change_done',
                             'users:logout']
                if name not in templates:
                    response = self.authorized_client.get(reverse(name))
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location_for_ayth_client(self):
        """Cтраницы доступные авторизованному пользователю."""
        for name, _, in self.page_names_with_templates:
            with self.subTest(page_name=name):
                response = self.authorized_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from users.forms import CreationForm


User = get_user_model()


class UsersViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client(enforce_csrf_checks=True)
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        page_names_with_templates = (
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
        for name, template, in page_names_with_templates:
            with self.subTest(page_name=name):
                response = self.authorized_client.get(reverse(name))
                self.assertTemplateUsed(response, template)

    def test_signup_show_correct_context(self):
        """Шаблон регистрации сформированы с верным контекстом"""
        response = self.authorized_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                self.assertIsInstance(response.context['form'], CreationForm)
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

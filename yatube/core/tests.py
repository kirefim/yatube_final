from django.test import TestCase
from django.urls import reverse


class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')

    def permission_denied(self):
        response = self.client.get(reverse('posts:post_edit'))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'core/403.html')

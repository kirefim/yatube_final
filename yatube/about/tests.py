from django.test import TestCase
from django.urls import reverse


class StaticURLTests(TestCase):

    def test_static_urls_uses_correct_template(self):
        """Проверка соответствия url реверсам."""
        page_names_with_urls = (
            ('about:author', '/about/author/'),
            ('about:tech', '/about/tech/'),
        )
        for name, url in page_names_with_urls:
            with self.subTest(page_name=name):
                self.assertEqual(reverse(name), url)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        page_names_with_templates = (
            ('about:author', 'about/author.html'),
            ('about:author', 'about/author.html'),
        )
        for name, template, in page_names_with_templates:
            with self.subTest(template=template):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template)

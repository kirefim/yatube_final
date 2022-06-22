from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from .. import models


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = models.User.objects.create_user(username='auth')
        cls.group = models.Group.objects.create(
            title='title',
            slug='test-slug',
        )
        cls.post = models.Post.objects.create(
            text='text',
            author=cls.user,
        )
        cls.page_names_with_templates = (
            ('posts:index', None, 'posts/index.html'),
            ('posts:group_list', (cls.group.slug,), (
                'posts/group_list.html')),
            ('posts:profile', (cls.user.username,), (
                'posts/profile.html')),
            ('posts:post_detail', (cls.post.pk,), (
                'posts/post_detail.html')),
            ('posts:post_edit', (cls.post.pk,), (
                'posts/create_post.html')),
            ('posts:post_create', None, 'posts/create_post.html'),
            ('posts:follow_index', None, 'posts/follow.html'),
            ('posts:profile_follow', (cls.user.username,), (
                'posts/profile.html')),
            ('posts:profile_unfollow', (cls.user.username,), (
                'posts/profile.html')),
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_request_unexisting_page(self):
        """Проверка на запрос к несуществующей странице."""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # Проверка соответствия хардкор ссылок реверсам
    def test_urls_equal_reverse_urls(self):
        """Проверка соответствия url реверсам."""
        page_names_with_urls = (
            ('posts:index', None, '/'),
            ('posts:group_list', (self.group.slug,), (
                f'/group/{self.group.slug}/')),
            ('posts:profile', (self.user.username,), (
                f'/profile/{self.user.username}/')),
            ('posts:post_detail', (self.post.pk,), (
                f'/posts/{self.post.pk}/')),
            ('posts:post_edit', (self.post.pk,), (
                f'/posts/{self.post.pk}/edit/')),
            ('posts:post_create', None, '/create/'),
            ('posts:follow_index', None, '/follow/'),
            ('posts:profile_follow', (self.user.username,), (
                f'/profile/{self.user.username}/follow/')),
            ('posts:profile_unfollow', (self.user.username,), (
                f'/profile/{self.user.username}/unfollow/')),
        )
        for name, args, url, in page_names_with_urls:
            with self.subTest(url=url):
                self.assertEqual(reverse(name, args=args), url)

    # Проверка вызова корректных шаблонов
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        page_names = (
            'posts:profile_follow',
            'posts:profile_unfollow',
        )
        for name, args, template, in self.page_names_with_templates:
            with self.subTest(page_name=name):
                if name not in page_names:
                    response = self.authorized_client.get(
                        reverse(name, args=args))
                    self.assertTemplateUsed(response, template)

    # Проверка доступа к страницам для неавторизованного пользователя
    def test_urls_exists_at_desired_location(self):
        """Cтраницы доступные любому пользователю."""
        not_exist_names = (
            'posts:post_edit',
            'posts:post_create',
            'posts:follow_index',
            'posts:profile_follow',
            'posts:profile_unfollow'
        )
        for name, args, _ in self.page_names_with_templates:
            with self.subTest(page_name=name):
                if name in not_exist_names:
                    reverse_login = reverse('users:login')
                    reverse_name = reverse(name, args=args)
                    response = self.client.get(
                        reverse_name,
                        follow=True)
                    self.assertRedirects(
                        response, (f'{reverse_login}?next={reverse_name}'))
                else:
                    response = self.client.get(
                        reverse(name, args=args))
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверка доступа к страницам для автора
    def test_urls_exists_at_desired_location_for_author(self):
        """Cтраницы доступные автору."""
        for name, args, _ in self.page_names_with_templates:
            with self.subTest(page_name=name):
                response = self.authorized_client.get(
                    reverse(name, args=args))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверка доступа к страницам для авторизованного клиента
    def test_urls_exists_at_desired_location_for_author(self):
        """Cтраницы доступные авторизованному пользователю."""
        redirect_pages = (
            'posts:post_edit',
            'posts:profile_follow',
            'posts:profile_unfollow'
        )
        user = models.User.objects.create_user(username='new auth')
        self.authorized_client.force_login(user)
        for name, args, _ in self.page_names_with_templates:
            with self.subTest(page_name=name):
                if name not in redirect_pages:
                    response = self.authorized_client.get(
                        reverse(name, args=args))
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                elif name == 'posts:post_edit':
                    response = self.authorized_client.get(
                        reverse(name, args=args),
                        follow=True)
                    self.assertRedirects(
                        response, reverse('posts:post_detail', args=args))
                else:
                    response = self.authorized_client.get(
                        reverse(name, args=args),
                        follow=True)
                    self.assertRedirects(
                        response, reverse('posts:profile', args=args))

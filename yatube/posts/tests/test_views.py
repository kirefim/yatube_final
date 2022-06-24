from http import HTTPStatus
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.forms import PostForm, CommentForm

from .. import models


TEMP_MEDIA_ROOT = tempfile.mkdtemp(
    dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = models.User.objects.create_user(username='auth')
        cls.group = models.Group.objects.create(
            title='title',
            slug='test-slug',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = models.Post.objects.create(
            text='text',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def correct_context(self, response, is_post_detail=False):
        if not is_post_detail:
            data = response.context['page_obj'][0]
        else:
            data = response.context['post']
        self.assertEqual(data.text, self.post.text)
        self.assertEqual(data.author, self.user)
        self.assertEqual(data.group, self.group)
        self.assertEqual(data.pub_date, self.post.pub_date)
        self.assertContains(response, '<img')

    def test_index_show_correct_context(self):
        """Шаблон index сформированы с верным контекстом"""
        response = self.client.get(reverse('posts:index'))
        self.correct_context(response)

    def test_follow_show_correct_context(self):
        """Шаблон follow сформированы с верным контекстом"""
        folower = models.User.objects.create_user(username='tester')
        self.authorized_client.force_login(folower)
        models.Follow.objects.create(user=folower, author=self.user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.correct_context(response)

    def test_following(self):
        """Проверка корректной работы подписок"""
        folower_count = models.Follow.objects.all().count()
        folower = models.User.objects.create_user(username='tester')
        self.authorized_client.force_login(folower)
        response = self.authorized_client.get(
            reverse('posts:profile_follow', args=(self.user.username,)),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user.username,))
        )
        self.assertEqual(folower.follower.count(), folower_count + 1)

    def test_unfollowing(self):
        """Проверка корректной работы отписок"""
        folower = models.User.objects.create_user(username='tester')
        models.Follow.objects.create(user=folower, author=self.user)
        self.authorized_client.force_login(folower)
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow', args=(self.user.username,)),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user.username,))
        )
        self.assertEqual(folower.following.count(), 0)

    def test_group_show_correct_context(self):
        """Шаблон group сформированы с верным контекстом"""
        response = self.client.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        with self.subTest():
            self.correct_context(response)
            self.assertEqual(response.context['group'], self.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформированы с верным контекстом"""
        response = self.client.get(
            reverse('posts:profile', args=(self.user.username,)))
        with self.subTest():
            self.correct_context(response)
            self.assertEqual(response.context['author'], self.user)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформированы с верным контекстом"""
        response = self.client.get(
            reverse('posts:post_detail', args=(self.post.pk,)))
        self.correct_context(response, True)

    def test_post_detail_show_comments(self):
        """В шаблон post_detail передаются комменты к посту"""
        comment = models.Comment.objects.create(
            post=self.post,
            author=self.user,
            text='cool',
        )
        response = self.client.get(
            reverse('posts:post_detail', args=(self.post.pk,)))
        data = response.context['comments'][0]
        with self.subTest():
            self.assertEqual(data.post, self.post)
            self.assertEqual(data.author, self.user)
            self.assertEqual(data.text, comment.text)
        form_fields = {'text': forms.fields.CharField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                self.assertIsInstance(response.context['form'], CommentForm)
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_or_edit_show_correct_context(self):
        """Шаблон post_create и post_edit сформированы с верным контекстом"""
        page_names = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', args=(self.post.pk,)),
        )
        for page in page_names:
            response = self.authorized_client.get(page)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
                'image': forms.fields.ImageField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    self.assertIsInstance(response.context['form'], PostForm)
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_create_new_post(self):
        """Созданный пост не отображается в новой группе"""
        empty_group = models.Group.objects.create(
            title='new title',
            slug='new_slug',
        )
        form_data = {
            'text': 'new text',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', args=(empty_group.slug,)))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.context['page_obj']), 0)


COUNT_POST = 13


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = models.User.objects.create_user(username='auth')
        cls.group = models.Group.objects.create(
            title='title',
            slug='test-slug',
        )
        for text in range(COUNT_POST):
            cls.post = models.Post.objects.create(
                text=str(text),
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        cache.clear()
        self.page_names = (
            ('posts:index', ()),
            ('posts:group_list', (self.group.slug,)),
            ('posts:profile', (self.user.username,)),
            ('posts:follow_index', None),
        )
        self.pages = (
            ('?page=1', settings.SLICE),
            ('?page=2', COUNT_POST - settings.SLICE)
        )
        self.folower = models.User.objects.create_user(username='tester')
        models.Follow.objects.create(user=self.folower, author=self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.folower)

    def test_page_contains_right_records(self):
        """Проверка паджинатора: посты разбиваются по страницам"""
        for name, args in self.page_names:
            with self.subTest(page_name=name):
                for page, posts_amt in self.pages:
                    with self.subTest(page_num=page):
                        response = self.authorized_client.get(
                            reverse(name, args=args) + page)
                        self.assertEqual(
                            len(response.context['page_obj']), posts_amt)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CachingViewsTests(TestCase):
    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.user = models.User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_cached(self):
        """В шаблоне index список записей кешируется"""
        post = models.Post.objects.create(
            text='cached_text',
            author=self.user,
        )
        response1 = self.client.get(reverse('posts:index'))
        post.delete()
        response2 = self.client.get(reverse('posts:index'))
        self.assertEqual(response2.content, response1.content)
        cache.clear()
        response3 = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response3.content, response1.content)

    def test_follow_index_cached(self):
        """В шаблоне follow_index список записей кешируется"""
        post = models.Post.objects.create(
            text='cached_text',
            author=self.user,
        )
        folower = models.User.objects.create_user(username='tester')
        models.Follow.objects.create(user=folower, author=self.user)
        self.authorized_client.force_login(folower)

        response1 = self.authorized_client.get(reverse('posts:follow_index'))
        post.delete()
        response2 = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(response2.content, response1.content)
        cache.clear()
        response3 = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotEqual(response3.content, response1.content)

from http import HTTPStatus
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.forms import PostForm

from .. import models


TEMP_MEDIA_ROOT = tempfile.mkdtemp(
    dir=settings.MEDIA_ROOT)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
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
            group=cls.group,
        )
        cls.form = PostForm()

    def tearDown(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    def test_create_new_post_in_DB(self):
        """Созданный пост записывается в БД"""
        posts_count = models.Post.objects.count()
        form_data = {
            'text': 'text2',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=(self.user.username,)))
        self.assertEqual(models.Post.objects.count(), posts_count + 1)
        post = models.Post.objects.first()
        with self.subTest():
            self.assertEqual(post.text, form_data['text'])
            self.assertEqual(post.group, self.group)
            self.assertEqual(post.author, self.user)
            self.assertEqual(post.image.name, f'posts/{self.uploaded.name}')
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        posts_count = models.Post.objects.count()
        self.assertEqual(models.Post.objects.count(), posts_count)

    def test_edit_post_in_DB(self):
        """Обновление поста в БД"""
        posts_count = models.Post.objects.count()
        new_group = models.Group.objects.create(
            title='new group',
            slug='new_group',
        )
        form_data = {
            'text': 'text2',
            'group': new_group.pk,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', args=(self.post.pk,)))
        self.assertEqual(models.Post.objects.count(), posts_count)
        post = models.Post.objects.first()
        with self.subTest():
            self.assertEqual(post.text, form_data['text'])
            self.assertEqual(post.group, new_group)
            self.assertEqual(post.author, self.user)
            self.assertEqual(post.image.name, f'posts/{self.uploaded.name}')
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.group.pk,)),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_commenting_post(self):
        """Пост комментируется"""
        comments_count = models.Comment.objects.count()
        form_data = {
            'text': 'text2',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=(self.post.pk,)),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse('posts:post_detail', args=(self.post.pk,)))
        self.assertEqual(models.Comment.objects.count(), comments_count + 1)
        comment = self.post.comments.first()
        with self.subTest():
            self.assertEqual(comment.post, self.post)
            self.assertEqual(comment.text, form_data['text'])
            self.assertEqual(comment.author, self.user)
        response = self.client.post(
            reverse('posts:add_comment', args=(self.post.pk,)),
            data=form_data,
            follow=True
        )
        comments_count = models.Comment.objects.count()
        self.assertEqual(models.Comment.objects.count(), comments_count)

    def test_title_label(self):
        """Проверка label полей формы"""
        page_names = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', args=(self.post.pk,)),
        )
        form_field = ('text', 'group', 'image')
        for page in page_names:
            response = self.authorized_client.get(page)
            for field in form_field:
                with self.subTest(field=field):
                    label_template = response.context['form'][field].label
                    label_form = self.form[field].label
                    self.assertEqual(label_template, label_form)

    def test_title_help_text(self):
        """Проверка help_text полей формы"""
        page_names = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', args=(self.post.pk,)),
        )
        form_field = ('text', 'group', 'image')
        for page in page_names:
            response = self.authorized_client.get(page)
            for field in form_field:
                with self.subTest(field=field):
                    label_template = response.context['form'][field].help_text
                    label_form = self.form[field].help_text
                    self.assertEqual(label_template, label_form)

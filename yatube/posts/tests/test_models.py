from django.test import TestCase

from .. import models


class TestModels(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = models.User.objects.create_user(username='auth')
        cls.group = models.Group.objects.create(
            title='Ж' * 201,
            slug='Слаг',
        )
        cls.post = models.Post.objects.create(
            text='Ж' * 31,
            author=cls.user,
        )

    def test_post_and_group_fields_is_truncated(self):
        """В поле __str__  объекта group записано значение поля group.title.
           В поле __str__  объекта post записано усеченное
        значение поля post.text."""
        max_length = self.group._meta.get_field('title').max_length
        LIMIT = 30
        with self.subTest():
            self.assertEqual(self.group.title[:max_length], str(self.group))
            self.assertEqual(self.post.text[:LIMIT], str(self.post))

    def test_post_and_group_verboses_name(self):
        """__str__ Post, Group имеет значение verbose_name"""
        verbose_post = self.post._meta.verbose_name
        verbose_group = self.group._meta.verbose_name
        with self.subTest():
            self.assertEqual(verbose_post, str(models.Post._meta.verbose_name))
            self.assertEqual(
                verbose_group,
                str(models.Group._meta.verbose_name))

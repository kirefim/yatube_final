from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from core.models import CreatedModel


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Название группы',
        unique=True,
        max_length=200,)
    slug = models.SlugField(
        'Ссылка на группу',
        unique=True,)
    description = models.TextField(
        'Описание группы',
        default='Описание группы',)

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self) -> str:
        return self.title[:self._meta.get_field('title').max_length]


class Post(CreatedModel):
    text = models.TextField(
        'Текст поста',
        default='--None--',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста')
    group = models.ForeignKey(
        Group,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self) -> str:
        LIMIT = 30
        return self.text[:LIMIT]

    def get_absolute_url(self):
        return reverse('posts:post_detail', args=(self.pk,))


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    text = models.TextField(
        'Текст комментария',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = "Коммент"
        verbose_name_plural = "Комменты"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписка',
    )

    class Meta:
        verbose_name = "Подписки"
        verbose_name_plural = "Подписки"

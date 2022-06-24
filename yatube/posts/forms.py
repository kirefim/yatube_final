from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'Введите текст создаваемого поста',
            'group': 'Укажите группу, в которой будет опубликован пост',
            'image': 'Прикрепите картинку к посту'
        }
        labels = {
            'text': 'Текст',
            'group': 'Группа',
            'image': 'Картинка'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Введите текст комментария',
        }
        labels = {
            'text': 'Текст',
        }

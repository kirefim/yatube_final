from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group', 'image')
    search_fields = ('text', 'group', 'author')
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description', 'slug',)
    search_fields = ('title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pub_date', 'post', 'author', 'text',)
    search_fields = ('post', 'text', 'author')
    list_filter = ('pub_date',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = ('user', 'author',)

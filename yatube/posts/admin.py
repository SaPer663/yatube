from django.conf import settings
from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Отображение модели Пост в админке."""

    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Отображение модели Группа в админке."""

    list_display = ('pk', 'description', 'title', 'slug',)
    search_fields = ('description',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Модель Коммент."""
    list_display = ('text', 'post', 'author', 'created',)
    search_fields = ('text',)
    list_filter = ('created',)


@admin.register(Follow)
class Follow(admin.ModelAdmin):
    """Модель Подпискаю"""
    list_display = ('user', 'author',)

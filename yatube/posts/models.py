from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель Группа постов."""

    title = models.CharField(max_length=200, verbose_name='заголовок')
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='часть URL-адреса'
    )
    description = models.TextField(verbose_name='описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:100]
        super().save(*args, **kwargs)


class Post(models.Model):
    """Модель Пост."""

    text = models.TextField(
        verbose_name='текст',
        help_text='Текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        verbose_name='картинка',
        help_text='Картинка для поста',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    """Модель комментарий пользователя."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='комментарий',
        help_text='Комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор',
        help_text='Автор комментария'

    )
    text = models.TextField(
        verbose_name='текст',
        help_text='Текст комментария'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата и время создания',
        help_text='Дата и время создания комментария'
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
        help_text='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following'
            ),
            models.CheckConstraint(
                name='prevent_self_follow',
                check=~models.Q(user=models.F('author')),
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'author: {self.author.username} - user: {self.user.username}'

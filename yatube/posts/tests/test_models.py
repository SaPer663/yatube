import re

from django.test import TestCase

from ..models import Group
from .setup_data import (
    create_comment, create_follow, create_group, create_post, create_user,
)


class PostsModelsTest(TestCase):
    """Проверяет модель Post."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = create_user('Simple_user')
        cls.user_author = create_user('Author')
        cls.group = create_group(1)
        cls.group_without_slug = Group.objects.create(
            title='Ж !@#$%^&*()[]{}-Ж' * 100,
            description='Тестовое описание'
        )
        cls.post = create_post(author=cls.user, group=cls.group)
        cls.comment = create_comment(post=cls.post, author=cls.user)
        cls.follow = create_follow(follower=cls.user, author=cls.user_author)

    def test_models_have_correct_object_names(self):
        """Проверяет, что у моделей корректно работает __str__."""
        comment = PostsModelsTest.comment
        follow = PostsModelsTest.follow
        group = PostsModelsTest.group
        post = PostsModelsTest.post
        models_method_str = {
            post: post.text[:15],
            group: group.title,
            comment: comment.text[:15],
            follow: (f'author: {follow.author.username}'
                     f' - user: {follow.user.username}')
        }
        for model, expected_value in models_method_str.items():
            with self.subTest(model=model):
                self.assertEqual(
                    str(model), expected_value
                )

    def test_text_convert_to_slug(self):
        """Содержимое поля title преобразуется в slug."""
        slug = PostsModelsTest.group_without_slug.slug
        match = re.search(r'[^-a-zA-Z0-9_]+', fr'{slug}')
        self.assertIsNone(match)

    def test_text_slug_max_length_not_exceed(self):
        """Длинный slug обрезается и не превышает max_length
        поля slug в модели.
        """
        group = PostsModelsTest.group_without_slug
        max_length_slug = group._meta.get_field('slug').max_length
        self.assertEqual(len(group.slug), max_length_slug)

import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase, override_settings

from ..forms import CommentForm, PostForm
from ..models import Post
from .setup_data import (
    ViewNamePatternURL, comparison_of_class_attributes_values, create_comment,
    create_follow, create_group, create_post, create_user, image_path,
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
view_name = ViewNamePatternURL()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTest(TestCase):
    """Тесты функций представлений posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = create_user(username='Author')
        cls.user_follower = create_user(username='Follower')
        cls.group = create_group(1)

        cls.post_with_other_group = create_post(
            author=cls.user,
            group=create_group(2)
        )
        cls.post = create_post(
            author=cls.user,
            group=cls.group,
            image=image_path('small.gif'))
        cls.comment = create_comment(cls.post, cls.user)
        cls.follow = create_follow(follower=cls.user_follower, author=cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTest.user)
        self.authorized_follower = Client()
        self.authorized_follower.force_login(PostsViewsTest.user_follower)

    def tearDown(self):
        super().tearDown()
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        names_template_pages = {
            view_name.index: 'posts/index.html',
            view_name.group_list(
                PostsViewsTest.group.slug
            ): 'posts/group_list.html',
            view_name.profile(
                PostsViewsTest.user.username
            ): 'posts/profile.html',
            view_name.post_detail(
                PostsViewsTest.post.id
            ): 'posts/post_detail.html',
            view_name.post_create: 'posts/post_create.html',
            view_name.post_edit(
                PostsViewsTest.post.id
            ): 'posts/post_create.html',
            view_name.follow_index: 'posts/follow.html'
        }
        for reverse_name, template in names_template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_context_contains_model_expected_fields(self):
        """При выводе поста, все его поля передаются в словаре context страниц
        index, group_list, profile, follow.
        """
        reverse_names_counts = {
            view_name.index: ['index', Post.objects.count()],
            view_name.group_list(
                PostsViewsTest.group.slug
            ): [
                'group_list',
                Post.objects.filter(group=PostsViewsTest.group).count()
            ],
            view_name.profile(
                PostsViewsTest.user.username
            ): [
                'profile',
                Post.objects.filter(author=PostsViewsTest.user).count()
            ],
            view_name.follow_index: [
                'follow',
                PostsViewsTest.user.posts.count()]
        }
        for reverse_name, (name, count) in reverse_names_counts.items():
            with self.subTest(name=name):
                response = self.authorized_follower.get(reverse_name)
                self.assertIn('page_obj', response.context)
                self.assertEqual(
                    response.context['page_obj'].paginator.count,
                    count
                )
                comparison_of_class_attributes_values(
                    self,
                    response.context['page_obj'][0],
                    PostsViewsTest.post
                )

    def test_index_page_cache(self):
        """Контент страницы index кешируется."""
        create_post(author=PostsViewsTest.user, text='New text post')

        response = self.client.get(view_name.index)
        response_post = response.context.get('page_obj')[0]
        self.assertContains(response, response_post)

        response_post.delete()

        response = self.client.get(view_name.index)
        self.assertContains(response, response_post.text)

        cache.clear()

        response = self.client.get(view_name.index)
        self.assertNotContains(response, response_post.text)

    def test_posts_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        group_obj = PostsViewsTest.group
        response = self.authorized_client.get(
            view_name.group_list(group_obj.slug)
        )
        self.assertIn('group', response.context)
        post_group = response.context['group']
        comparison_of_class_attributes_values(
            self,
            model=group_obj,
            expected=post_group
        )

        list_posts = response.context.get('page_obj')
        for one_post in list_posts:
            with self.subTest(post=str(one_post)):
                self.assertEqual(one_post.group, post_group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            view_name.profile(PostsViewsTest.user)
        )
        self.assertIn('author', response.context)
        post_author = response.context['author']
        self.assertEqual(post_author, PostsViewsTest.user)

        list_posts = response.context.get('page_obj')
        for one_post in list_posts:
            with self.subTest(post=str(one_post)):
                self.assertEqual(one_post.author, post_author)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        post_obj = PostsViewsTest.post
        response = self.authorized_client.get(
            view_name.post_detail(post_obj.id)
        )
        self.assertIn('post', response.context)
        post = response.context.get('post')
        comparison_of_class_attributes_values(
            self,
            model=post,
            expected=post_obj
        )
        comparison_of_class_attributes_values(
            self,
            post.comments.latest('created'),
            PostsViewsTest.comment)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context.get('form'), CommentForm)

    def test_add_comment_be_commented_an_authorized_client(self):
        """Комментировать посты может только авторизованный пользователь"""
        number_of_post_comments = PostsViewsTest.post.comments.count()
        text = 'Новый комментарий'
        self.authorized_client.post(
            view_name.add_comment(PostsViewsTest.post.id),
            data={'text': text},
            follow=True
        )
        new_number_of_post_comments = PostsViewsTest.post.comments.count()
        self.assertEqual(
            PostsViewsTest.post.comments.count(),
            number_of_post_comments + 1
        )
        self.client.post(
            view_name.add_comment(PostsViewsTest.post.id),
            data={'text': text},
            follow=True
        )
        self.assertEqual(
            PostsViewsTest.post.comments.count(),
            new_number_of_post_comments
        )

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(view_name.post_create)
        for field in PostForm().fields:
            with self.subTest(field=field):
                expected_fields = response.context.get('form').fields.keys()
                self.assertIn(field, expected_fields)

    def test_post_create_method_post(self):
        """Проверка создания нового поста."""
        last_post_in_db = Post.objects.order_by('-id').first()
        text = 'Новый пост'
        image = image_path('new_image.gif')
        response = self.authorized_client.post(
            view_name.post_create,
            data={
                'text': text,
                'group': PostsViewsTest.group.id,
                'image': image
            },
            follow=True
        )
        self.assertRedirects(
            response,
            view_name.profile(PostsViewsTest.user.username)
        )
        new_post = Post.objects.order_by('-id').first()
        self.assertNotEqual(new_post, last_post_in_db)

        reverse_names = {
            'index': view_name.index,
            'post_group': view_name.group_list(PostsViewsTest.group.slug),
            'post_author_profile': view_name.profile(
                PostsViewsTest.user.username
            )
        }
        for name, reverse_name in reverse_names.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse_name)
                post = response.context.get('page_obj')[0]
                comparison_of_class_attributes_values(self, new_post, post)

        response = self.authorized_client.get(view_name.group_list(
            PostsViewsTest.post_with_other_group.group.slug
        ))
        post = response.context.get('page_obj')[0]
        self.assertNotEqual(post.text, text)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        post = PostsViewsTest.post
        response = self.authorized_client.get(view_name.post_edit(
            post.id
        ))
        self.assertIn('form', response.context)
        expected_post = response.context.get('form').instance
        comparison_of_class_attributes_values(self, post, expected_post)

    def test_post_edit_method_post(self):
        """Проверка изменения поста."""
        group_id = PostsViewsTest.group.id
        text = 'Изменённый пост'
        post_id = PostsViewsTest.post.id
        response = self.authorized_client.post(
            view_name.post_edit(post_id),
            data={'text': text, 'group': group_id},
            follow=True
        )
        self.assertRedirects(response, view_name.post_detail(post_id))
        modified_post = get_object_or_404(Post, id=post_id)
        self.assertIsNotNone(modified_post)
        self.assertEqual(modified_post.text, text)
        self.assertEqual(modified_post.group.id, group_id)

    def test_authorized_user_can_subscribe(self):
        """Авторизованный пользователь может подписываться
        на других пользователей.
        """
        author = create_user(username='popular author')
        create_post(
            author=author,
            text='New post',
            image=image_path('image.gif')
        )
        zero_subscribers_of_author = author.following.count()
        self.assertEqual(0, zero_subscribers_of_author)
        self.authorized_follower.get(view_name.profile_follow(author.username))
        self.assertEqual(
            author.following.count(),
            zero_subscribers_of_author + 1
        )
        self.assertTrue(
            PostsViewsTest.user_follower.follower.filter(
                author_id=author.id
            ).exists()
        )

    def test_authorized_user_can_unsubscribe(self):
        """Авторизованный пользователь может отписываться
        от других пользователей.
        """
        number_subscribers_of_author = PostsViewsTest.user.following.count()
        self.assertNotEqual(0, number_subscribers_of_author)
        self.authorized_follower.get(
            view_name.profile_unfollow(PostsViewsTest.user.username)
        )
        self.assertEqual(
            PostsViewsTest.user.following.count(),
            number_subscribers_of_author - 1
        )
        self.assertFalse(
            PostsViewsTest.user_follower.follower.filter(
                author_id=PostsViewsTest.user.id
            ).exists()
        )

    def test_new_post_appears_at_subscriber_and_no_at_unsubscriber(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан.
        """
        author = create_user(username='popular author')
        first_post = create_post(
            author=author,
            text='First post',
            image=image_path('image.gif')
        )
        response = self.authorized_client.get(view_name.follow_index)
        self.assertEqual(0, response.context['page_obj'].paginator.count)
        self.authorized_client.get(view_name.profile_follow(
            author.username
        ))
        response = self.authorized_client.get(view_name.follow_index)
        self.assertEqual(1, response.context['page_obj'].paginator.count)
        comparison_of_class_attributes_values(
            self,
            first_post,
            response.context.get('page_obj')[0])
        second_post = create_post(
            author=author,
            text='Second post',
            image=image_path('image.gif')
        )
        response = self.authorized_client.get(view_name.follow_index)
        self.assertEqual(2, response.context['page_obj'].paginator.count)
        comparison_of_class_attributes_values(
            self,
            second_post,
            response.context.get('page_obj')[0])
        response = self.authorized_follower.get(view_name.follow_index)
        last_post = response.context.get('page_obj')[0]
        self.assertNotEqual(second_post.id, last_post.id)

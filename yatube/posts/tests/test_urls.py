from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from .setup_data import (
    create_comment, create_follow, create_group, create_post, create_user,
)


class PostURLTest(TestCase):
    """Проверяет доступность страниц и названия шаблонов приложения posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_without_post = create_user(username='Simple_user')
        cls.user_author = create_user(username='Author')
        cls.group = create_group(1)
        cls.post = create_post(author=cls.user_author, group=cls.group)
        cls.comment = create_comment(
            post=cls.post,
            author=cls.user_without_post
        )
        cls.follow = create_follow(
            follower=cls.user_without_post,
            author=cls.user_author
        )

    def setUp(self):
        self.authorized_client = Client()
        self.author_authorized_client = Client()
        self.authorized_client.force_login(PostURLTest.user_without_post)
        self.author_authorized_client.force_login(PostURLTest.user_author)

    def tearDown(self):
        super().tearDown()
        cache.clear()

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_group_slug_url_exists_at_desired_location(self):
        """Страница /group/<slug:slug>/ доступна любому пользователю."""
        response = self.client.get(f'/group/{PostURLTest.group.slug}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_profile_username_url_exists_at_desired_location(self):
        """Страница /profile/<str:username>/ доступна любому пользователю."""
        response = self.client.get(
            f'/profile/{self.user_author.username}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_posts_detail_url_exists_at_desired_location(self):
        """Страница /posts/<int:post_id>/ доступна любому пользователю."""
        response = self.client.get(f'/posts/{PostURLTest.post.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.author_authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exists_at_desired_location_author(self):
        """Страница /posts/<int:post_id>/edit/ доступна пользователю-автору."""
        response = self.author_authorized_client.get(
            f'/posts/{PostURLTest.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_url_redirect_authorized(self):
        """Страница /posts/<int:post_id>/edit/ перенаправляет
        авторизованного пользователя не автора.
        """
        response = self.authorized_client.get(
            f'/posts/{PostURLTest.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_url_redirect_anonymous(self):
        """Страница /posts/<int:post_id>/edit/ перенаправляет анонимного
        пользователя.
        """
        response = self.client.get(f'/posts/{PostURLTest.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_follow_url_redirect_anonymous(self):
        """Страница /follow/ перенаправляет анонимного
        пользователя.
        """
        response = self.client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_comment_url_redirect_anonymous(self):
        """Страница /posts/<int:post_id>/comment/ перенаправляет анонимного
        пользователя.
        """
        response = self.client.get(f'/posts/{PostURLTest.post.id}/comment/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_username_follow_url_redirect_anonymous(self):
        """Страница /profile/<str:username>/follow'/ перенаправляет анонимного
        пользователя.
        """
        response = self.client.get(
            f'/profile/{self.user_author.username}/follow/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_username_unfollow_url_redirect_anonymous(self):
        """Страница /profile/<str:username>/unfollow'/ перенаправляет
        анонимного пользователя.
        """
        response = self.client.get(
            f'/profile/{self.user_author.username}/unfollow/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unexisting_page_return_not_found(self):
        """Несуществующая страница /unexisting_page/ вернёт ошибку 404."""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{PostURLTest.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user_author.username}/': 'posts/profile.html',
            f'/posts/{PostURLTest.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/post_create.html',
            f'/posts/{PostURLTest.post.id}/edit/': 'posts/post_create.html',
            '/follow/': 'posts/follow.html',
            '/unexisting_page/': 'core/404.html'

        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.author_authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

from http import HTTPStatus

from django.contrib.auth.tokens import default_token_generator
from django.test import Client, TestCase
from django.utils.http import int_to_base36

from posts.tests.setup_data import create_user


class UsersURLsTest(TestCase):
    """Проверяет доступность страниц и названия шаблонов приложения users."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = create_user(username='Simple_user')
        cls.other_user = create_user(username='Other')

    def setUp(self):
        self.authorized_client = Client()
        self.other_authorized_client = Client()
        self.authorized_client.force_login(UsersURLsTest.user)
        self.other_authorized_client.force_login(UsersURLsTest.other_user)

    def test_signup_url_exists_at_desired_location(self):
        """Страница /auth/signup/ доступна любому пользователю."""
        response = self.client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_url_exists_at_desired_location(self):
        """Страница /auth/login/ доступна любому пользователю."""
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_url_exists_at_desired_location(self):
        """Страница /auth/logout/ доступна любому пользователю."""
        response = self.client.get('/auth/logout/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_url_exists_at_desired_location(self):
        """Страница /auth/password_reset/ доступна любому пользователю."""
        response = self.client.get('/auth/password_reset/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_done_url_exists_at_desired_location(self):
        """Страница /auth/password_reset/done/ доступна любому пользователю."""
        response = self.client.get('/auth/password_reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_done_url_exists_at_desired_location(self):
        """Страница /auth/reset/done/ доступна любому пользователю."""
        response = self.client.get('/auth/reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_url_exists_at_desired_location(self):
        """Страница /auth/password_change/ доступна авторизованному
        пользователю.
        """
        response = self.authorized_client.get('/auth/password_change/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_done_url_exists_at_desired_location(self):
        """Страница /auth/password_change/done/ доступна авторизованному
        пользователю.
        """
        response = self.authorized_client.get('/auth/password_change/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_token_url_exists_at_desired_location(self):
        """Страница /auth/reset/<uidb64>/<token>/ доступна авторизованному
        пользователю с верной ссылкой.
        """
        token = default_token_generator.make_token(UsersURLsTest.user)
        uid = int_to_base36(UsersURLsTest.user.id)
        response = self.authorized_client.get(f'/auth/reset/{uid}/{token}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_url_redirect_anonymous(self):
        """Страница /auth/password_change/ не доступна неавторизованному
        пользователю.
        """
        response = self.client.get('/auth/password_change/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_password_change_done_url_redirect_anonymous(self):
        """Страница /auth/password_change/done/ не доступна неавторизованному
        пользователю.
        """
        response = self.client.get('/auth/password_change/done/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_template(self):
        """Проверяем, что URL-адреса используют соответствующие шаблоны."""
        token = default_token_generator.make_token(UsersURLsTest.user)
        uid = int_to_base36(UsersURLsTest.user.id)
        templates_url_names = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            f'/auth/reset/{uid}/{token}/': (
                'users/password_reset_confirm.html'
            ),
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

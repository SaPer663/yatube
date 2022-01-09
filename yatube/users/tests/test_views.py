from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.http import int_to_base36

from posts.models import User
from posts.tests.setup_data import create_user


class UsersViewsTest(TestCase):
    """Проверяет views users."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = create_user(username='Simple_user')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(UsersViewsTest.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес используют соответствующие шаблоны."""
        token = default_token_generator.make_token(UsersViewsTest.user)
        uid = int_to_base36(UsersViewsTest.user.id)
        names_template_pages = {
            reverse('users:login'): 'users/login.html',
            reverse(
                'users:password_change'
            ): 'users/password_change_form.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:signup'): 'users/signup.html',
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': uid, 'token': token}
            ): 'users/password_reset_confirm.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
        }
        for reverse_name, template in names_template_pages.items():
            with self.subTest(reverse_names=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_users_signup_page_show_correct_context(self):
        """Шаблон signup сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('users:signup'))
        self.assertIn('form', response.context)

    def test_users_signup_method_post(self):
        """Проверка создания нового пользователя."""
        count_user = User.objects.count()
        username = 'Новенький'
        password1 = 'Valid123'
        password2 = password1
        response = self.client.post(
            reverse('users:signup'),
            data={
                'username': username,
                'password1': password1,
                'password2': password2
            }
        )
        self.assertIn(response.status_code, (301, 302))
        new_user = get_object_or_404(User, username=username)
        self.assertIsNotNone(new_user)
        self.assertEqual(User.objects.count(), count_user + 1)
        self.assertEqual(new_user.username, username)

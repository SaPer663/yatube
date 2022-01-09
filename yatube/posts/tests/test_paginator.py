from django.core.paginator import Page, Paginator
from django.test import TestCase

from .setup_data import (
    ViewNamePatternURL, create_group, create_user, one_of_thirteen_posts,
)

view_name = ViewNamePatternURL()


class PaginatorViewsTest(TestCase):
    """Тестирование паджинатора представленийю"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = create_user(username='NoName')
        cls.group = create_group(1)
        one_of_thirteen_posts(author=cls.user, group=cls.group)

    def test_paginators_view(self):
        """Проверка паджинаторов представлений."""
        reverse_names = {
            'index': view_name.index,
            'group_list': view_name.group_list(PaginatorViewsTest.group.slug),
            'profile': view_name.profile(PaginatorViewsTest.user.username)
        }
        for name, reverse_name in reverse_names.items():
            with self.subTest(name=name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)
                self.assertIsInstance(response.context['page_obj'], Page)
                self.assertIsInstance(
                    response.context['page_obj'].paginator, Paginator)

    def test_second_page_contains_three_records(self):
        """ На второй странице должно быть три поста."""
        reverse_names = {
            'index': view_name.index,
            'group_list': view_name.group_list(PaginatorViewsTest.group.slug),
            'profile': view_name.profile(PaginatorViewsTest.user.username)
        }
        for name, reverse_name in reverse_names.items():
            with self.subTest(name=name):
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)

from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class AboutURLsTest(TestCase):
    """Тестирует url."""

    def test_urls_exists_at_desired_location(self):
        """Проверка доступности адресов."""
        for url in ('/about/author/', '/about/tech/'):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                self.assertTemplateUsed(response, template)


class AboutViewsTests(TestCase):
    """Тестиреут views."""

    def test_about_pages_accessible_by_name(self):
        """URL, генерируемый при помощи имён about:author,
        about:tech доступен.
        """
        for url in ('about:author', 'about:tech'):
            with self.subTest(url=url):
                response = self.client.get(reverse(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_pages_uses_correct_template(self):
        """При запросе к about:author, about:tech
        применяются корректнве шаблоны.
        """
        names_template_pages = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html'
        }
        for name, template in names_template_pages.items():
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertTemplateUsed(response, template)

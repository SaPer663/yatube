import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings

from ..forms import CommentForm, PostForm
from ..models import Post
from .setup_data import (
    ViewNamePatternURL, create_group, create_post, create_user, image_path,
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
view_name = ViewNamePatternURL()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTest(TestCase):
    """Тесты форм posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = create_user(username='Author')
        cls.group = create_group(serial_number=1)
        cls.post = create_post(
            author=cls.user,
            group=cls.group,
            image=image_path(name='small.png')
        )
        cls.post_form = PostForm()
        cls.comment_form = CommentForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PostsFormTest.user)

    def test_pages_context_contains_correct_form(self):
        """Шаблоны post_create и post_edit содержат в контексте
        правильную форму.
        """
        names_reverse_urls = {
            'post_create': view_name.post_create,
            'post_edit': view_name.post_edit(PostsFormTest.post.id)
        }
        for name, reverse_url in names_reverse_urls.items():
            with self.subTest(name=name):
                response = self.author_client.get(reverse_url)
                form_expected = response.context.get('form')
                self.assertIsInstance(form_expected, PostForm)

    def test_create_post(self):
        """Валидная форма саздаст запись в базе."""
        number_of_posts = Post.objects.count()
        last_post_in_db = Post.objects.order_by('-id').first()
        text = 'Новый пост'
        image = image_path('new_image.gif')
        self.author_client.post(
            view_name.post_create,
            data={
                'text': text,
                'group': PostsFormTest.group.id,
                'image': image
            },
            follow=True
        )
        self.assertEqual(Post.objects.count(), number_of_posts + 1)
        new_post = Post.objects.order_by('-id').first()
        self.assertNotEqual(new_post, last_post_in_db)

    def test_create_comment(self):
        """Валидная форма саздаст запись в базе."""
        number_of_post_comments = PostsFormTest.post.comments.count()
        text = 'Новый комментарий'
        self.author_client.post(
            view_name.add_comment(PostsFormTest.post.id),
            data={'text': text},
            follow=True
        )
        self.assertEqual(
            PostsFormTest.post.comments.count(),
            number_of_post_comments + 1
        )

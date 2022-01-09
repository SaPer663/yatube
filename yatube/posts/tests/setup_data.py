from mixer.backend.django import mixer

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ..models import Comment, Follow, Group, Post, User


def image_path(name):
    """Сохраняет перданную последовательность байт, эмулируя
    сохранение картинки, и возвращает путь к ней.
    Принимает name: str вида `small.gif`.
    """
    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x02\x00'
        b'\x01\x00\x80\x00\x00\x00\x00\x00'
        b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
        b'\x00\x00\x00\x2C\x00\x00\x00\x00'
        b'\x02\x00\x01\x00\x00\x02\x02\x0C'
        b'\x0A\x00\x3B'
    )
    return SimpleUploadedFile(
        name=name,
        content=small_gif,
        content_type='image/gif'
    )


def create_user(username):
    """Создаёт и возвращает пользователя.
    Принимает обязательный аргумент username: str юзернейм пользователя.
    """
    return User.objects.create_user(username=username)


def create_group(serial_number):
    """Создаёт в базе и возвращает объект класса Group.
    Принимает обязательный аргумент serial_number: int, который
    используется для создания новой группы.
    """
    return Group.objects.create(
        title=f'Тестовая группа {serial_number}',
        slug=f'test-slug-{serial_number}',
        description=f'Тестовое описание {serial_number}',
    )


def create_post(author, text='*' * 20, group=None, image=None):
    """Создаёт и возвращает пост c текстом размером 20 символов `*`.
    Принимает обязательный аргумент author: User и не обязательные
    group: Group = None и text: str = '*' * 20.
    """
    return Post.objects.create(
        author=author,
        text=text,
        group=group,
        image=image
    )


def create_comment(post, author, text='Новый комментарий'):
    """Создаёт и возврищает комментарий к заданному посту.
    Принимает обязательные аргументы post: Post и author: User.
    Необязательный аргумент text: str поумолчанию равен `Новый комментарий`.
    """
    return Comment.objects.create(
        post=post,
        author=author,
        text=text
    )


def create_follow(follower, author):
    """Создаётв базе и возвращает запись, определяющую подписку на посты
    автора. Принимает обязательные аргументы follower: User и author: User.
    """
    return Follow.objects.create(
        user=follower,
        author=author
    )


def one_of_thirteen_posts(author, group=None):
    """ Создаёт 13 постов в одной группе и c одним автором.
    Принимает обязательный аргумент author: User и не обязательный
    group: Group. Поумолчанию group=None.
    Возвращает последний пост.
    """
    posts = mixer.cycle(13).blend(Post, author=author, group=group)
    return posts[-1]


def one_of_few_posts():
    """ Создаёт 15 постов и возвращает последний пост."""
    posts = mixer.cycle(15).blend(Post)
    return posts[-1]


def comparison_of_class_attributes_values(test_case_instance, model, expected):
    """Проверяет эквивалентность значений атрибутов классов."""
    try:
        model_fields = model.__dict__
        expected_fields = expected.__dict__
    except AttributeError as e:
        test_case_instance.fail(e)
    test_case_instance.assertEqual(model_fields.keys(), expected_fields.keys())
    for field in model_fields:
        if field.startswith('_'):
            continue
        with test_case_instance.subTest(field=field):
            test_case_instance.assertEqual(
                model.__dict__.get(field),
                expected.__dict__.get(field)
            )


class ViewNamePatternURL:
    """Возвращает ссылку на абсолютный путь (URL без имени домена),
    соответствующую заданному представлению и переданным параметрам.
    """

    @property
    def index(self):
        """Cсылка на абсолютный путь до страницы index."""
        return reverse('posts:index')

    @staticmethod
    def group_list(slug):
        """Cсылка на абсолютный путь до страницы group_list."""
        return reverse(
            'posts:group_list',
            kwargs={'slug': slug}
        )

    @staticmethod
    def profile(username):
        """Cсылка на абсолютный путь до страницы profile."""
        return reverse(
            'posts:profile',
            kwargs={'username': username}
        )

    @staticmethod
    def post_detail(id):
        """Cсылка на абсолютный путь до страницы post_detail."""
        return reverse(
            'posts:post_detail',
            kwargs={'post_id': id}
        )

    @property
    def post_create(self):
        """Cсылка на абсолютный путь до страницы post_create."""
        return reverse('posts:post_create')

    @staticmethod
    def post_edit(id):
        """Cсылка на абсолютный путь до страницы post_edit."""
        return reverse(
            'posts:post_edit',
            kwargs={'post_id': id}
        )

    @property
    def follow_index(self):
        """Cсылка на абсолютный путь до страницы follow_index."""
        return reverse('posts:follow_index')

    @staticmethod
    def profile_follow(username):
        """Cсылка на абсолютный путь до страницы profile_follow."""
        return reverse(
            'posts:profile_follow',
            kwargs={'username': username}
        )

    @staticmethod
    def profile_unfollow(username):
        """Cсылка на абсолютный путь до страницы profile_unfollow."""
        return reverse(
            'posts:profile_unfollow',
            kwargs={'username': username}
        )

    @staticmethod
    def add_comment(id):
        """Cсылка на абсолютный путь до страницы add_comment."""
        return reverse(
            'posts:add_comment',
            kwargs={'post_id': id}
        )

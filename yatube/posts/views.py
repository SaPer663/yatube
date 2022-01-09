from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from core.utils import create_paginator

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


@cache_page(settings.CACHE_TIMEOUT)
def index(request):
    """Возвращает главныю страницу с постами.
    Принимает обязательный обьект request.
    """
    posts_list = Post.objects.all()
    page_obj = create_paginator(request, posts_list)
    return render(request, 'posts/index.html', {'page_obj': page_obj})


def group_list(request, slug):
    """Возврашает страницу с постами заданной группы.
    Принимает обязательные обьект request и уникальную строку: slug.
    """
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = create_paginator(request, posts)
    return render(request, 'posts/group_list.html', {
        'page_obj': page_obj,
        'group': group
    })


def profile(request, username):
    """Возвращает страницу пользователя.
    Принимает обязательные обьект request и логин пользователя: username.
    """
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = create_paginator(request, posts)
    if not request.user.is_authenticated:
        return render(request, 'posts/profile.html', {
            'author': author,
            'page_obj': page_obj
        })
    following = request.user.follower.filter(author=author).exists()
    return render(request, 'posts/profile.html', {
        'author': author,
        'page_obj': page_obj,
        'following': following
    })


def post_detail(request, post_id):
    """Возвращает страницу поста.
    Принимает обязательные обьект request и id поста: post_id.
    """
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'form': form
    })


@login_required
def add_comment(request, post_id):
    """Обрабатывает форму создания комментария к посту.
    Принимает обязательные обьект request и id поста,
    который нужно прокомментировать: post_id.
    """
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return redirect('posts:post_detail', post_id=post_id)
    comment = form.save(commit=False)
    comment.post = post
    comment.author = request.user
    comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_create(request):
    """Возвращает страницу с формой для создания нового поста.
    Принимает обязательный обьект request.
    """
    form = PostForm(request.POST or None, request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/post_create.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user.username)


@login_required
def post_edit(request, post_id):
    """Возвращает страницу с формой редактирования поста.
    Принимает обязательные обьект request и id поста,
    который нужно отредактировать: post_id.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'posts/post_create.html', {'form': form})
    form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Возвращает страницу с постами авторов, на которых подписан
    текущий пользователь. Принимает обязательные обьект request.
    """
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = create_paginator(request, posts)
    return render(request, 'posts/follow.html', {'page_obj': page_obj})


@login_required
def profile_follow(request, username):
    """Реализует процесс подписки на интересного автора.
    Принимает обязательные обьект request и логин автора: username.
    """
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Реализует процес отписки от не интересного автора.
    Принимает обязательные обьект request и логин автора: username.
    """
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect('posts:profile', username=username)
    get_object_or_404(Follow, user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)

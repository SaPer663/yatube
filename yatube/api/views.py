from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from posts.models import Comment, Group, Post
from .mixins import FollowMixinViewSet
from .permissions import AuthorOrReadOnly
from .serializers import (
    CommentSerializer, FollowSerializer, GroupSerializer, PostSerializer,
)


class PostViewSet(ModelViewSet):
    """Перечисление или получение постов.
    При указании параметров limit: int и offset: int
    выдача производится с пагинацией.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(ModelViewSet):
    """Перечисление или получение комментариев на пост."""
    serializer_class = CommentSerializer
    permission_classes = (AuthorOrReadOnly,)

    def get_queryset(self):
        return Comment.objects.filter(post__id=self.kwargs.get('post_id'))

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            post=get_object_or_404(Post, id=self.kwargs.get('post_id'))

        )


class GroupViewSet(ReadOnlyModelViewSet):
    """Перечисление или получение группы для постов."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class FollowViewSet(FollowMixinViewSet):
    """Перечисление или получение всех подписок пользователя."""
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

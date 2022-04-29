from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class FollowMixinViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    """Вьюсет предоставляет базовые `create()`, `list()` экшены."""
    pass

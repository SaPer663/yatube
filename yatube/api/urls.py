from django.urls import include, path, re_path
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, FollowViewSet, GroupViewSet, PostViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
        description="Документация для приложения api проекта yatube",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router_v1 = DefaultRouter()
router_v1.register(r'posts', PostViewSet)
router_v1.register(r'groups', GroupViewSet)
router_v1.register(
    r'posts/(?P<post_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router_v1.register(r'follow', FollowViewSet, basename='follow')

urlpatterns = [
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
    path('v1/', include(router_v1.urls)),
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'
    ),
    re_path(
        r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'v1/redoc/',
        TemplateView.as_view(template_name='api/redoc.html'),
        name='redoc'
    ),
]

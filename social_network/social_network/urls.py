from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from posts.views import PostViewSet, CommentViewSet, LikeViewSet
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('posts/<int:post_id>/comments/', CommentViewSet.as_view({'post': 'create', 'get': 'list'}), name='comment-list'),
    path('posts/<int:post_id>/likes/', LikeViewSet.as_view({'post': 'create', 'get': 'list'}), name='like-list'),
    path('posts/<int:post_id>/likes/<int:pk>/', LikeViewSet.as_view({'delete': 'destroy'}), name='like-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

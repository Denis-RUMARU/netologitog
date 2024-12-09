from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from posts.models import Post, Comment, Like
from posts.serializers import PostSerializer, CommentSerializer, LikeSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        post = self.get_object()
        if post.author != self.request.user:
            raise PermissionDenied("У вас нет прав для редактирования этого поста")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("У вас нет прав для удаления этого поста")
        instance.delete()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return post.comments.all()

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])

        serializer.save(post=post)


class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Like.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        # Проверка, чтобы пользователь не ставил лайк на один и тот же пост несколько раз
        if Like.objects.filter(author=self.request.user, post=post).exists():
            raise serializers.ValidationError("Вы уже лайкнули этот пост.")
        serializer.save(post=post, author=self.request.user)

    def destroy(self, request, post_id=None, pk=None):
        post = get_object_or_404(Post, id=post_id)
        like = get_object_or_404(Like, post=post, author=request.user)
        like.delete()
        return Response({"message": "Лайк удален"}, status=status.HTTP_204_NO_CONTENT)


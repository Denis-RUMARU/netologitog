from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from drf_extra_fields.fields import Base64ImageField
from posts.models import Comment, Post, Like

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('text', 'created_at',)

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True, source='commented_post')
    likes_count = SerializerMethodField()
    image = Base64ImageField(required=False)

    def get_likes_count(self, post):

        return post.liked_post.count()

    class Meta:
        model = Post
        fields = ('id', 'text', 'image', 'created_at', 'comments', 'likes_count')

    def validate_text(self, value):

        if len(value) < 3:
            raise serializers.ValidationError("Текст поста должен содержать не менее 3 символов.")
        return value

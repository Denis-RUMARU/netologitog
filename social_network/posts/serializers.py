from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from drf_extra_fields.fields import Base64ImageField
from posts.models import Comment, Post, Like


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'created_at', 'author')

    def validate_text(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Текст комментария должен содержать не менее 3 символов.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        author = request.user


        validated_data.pop('author', None)

        comment = Comment.objects.create(author=author, **validated_data)
        return comment


class LikeSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Like
        fields = ('id', 'author', 'post', 'created_at')

    def validate(self, attrs):

        if Like.objects.filter(author=self.context['request'].user, post=attrs['post']).exists():
            raise serializers.ValidationError("Вы уже лайкнули этот пост.")
        return attrs


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)
    author = serializers.StringRelatedField(read_only=True)

    def get_likes_count(self, post):
        return post.likes.count()

    def get_comments_count(self, post):
        return post.comments.count()

    class Meta:
        model = Post
        fields = ('id', 'text', 'image', 'created_at', 'comments', 'likes', 'likes_count', 'comments_count', 'author')

    def validate_text(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Текст поста должен содержать не менее 3 символов.")
        return value

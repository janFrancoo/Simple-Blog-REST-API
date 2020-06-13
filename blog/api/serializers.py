from rest_framework import serializers
from django.contrib.auth.models import User
from blog.api.models import Like, Post


class PostSerializer(serializers.ModelSerializer):
    likes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='by'
     )

    class Meta:
        model = Post
        fields = ['id', 'created_at', 'title', 'content', 'author', 'likes']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'by', 'post']

class UserSerializer(serializers.ModelSerializer):
    posts = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='post-detail')

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'posts']

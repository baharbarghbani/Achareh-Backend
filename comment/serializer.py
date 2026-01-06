from rest_framework import serializers
from .models import Comment
from user.models import User
from ad.models import Ad


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content', 'rating', 'ad', 'performer']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class CommentListSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    ad_title = serializers.CharField(source='ad.title', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'rating', 'user', 'user_name', 'ad', 'ad_title', 'created_at']
        read_only_fields = ['user', 'created_at']


class CommentDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    ad_title = serializers.CharField(source='ad.title', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'rating', 'user', 'user_name', 'ad', 'ad_title', 'created_at']
        read_only_fields = ['user', 'created_at']
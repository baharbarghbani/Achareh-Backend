from rest_framework import serializers
from .models import Comment


class CommentReadSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    performer = serializers.SerializerMethodField()
    ad = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'rating', 'created_at', 'ad', 'user', 'performer']

    def get_user(self, obj):
        u = obj.user
        return {'id': u.id, 'username': u.username}

    def get_performer(self, obj):
        u = obj.performer
        return {'id': u.id, 'username': u.username}

    def get_ad(self, obj):
        return {'id': obj.ad_id, 'title': obj.ad.title}


class CommentCreateSerializer(serializers.ModelSerializer):
    ad_id = serializers.IntegerField()
    performer_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ['content', 'rating', 'ad_id', 'performer_id']

    def create(self, validated_data):
        request = self.context['request']
        return Comment.objects.create(
            user=request.user,
            ad_id=validated_data['ad_id'],
            performer_id=validated_data['performer_id'],
            content=validated_data['content'],
            rating=validated_data['rating'],
        )

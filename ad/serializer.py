from rest_framework import serializers
from .models import Ad


class AdReadSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()
    performer = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = [
            'id', 'title', 'description', 'category', 'status', 'date_added',
            'creator', 'performer', 'execution_time', 'execution_location'
        ]

    def get_creator(self, obj):
        return {'id': obj.creator_id, 'username': obj.creator.username}

    def get_performer(self, obj):
        if obj.performer_id is None:
            return None
        return {'id': obj.performer_id, 'username': obj.performer.username}


class AdCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'category', 'execution_time', 'execution_location']


class AdUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'category', 'status', 'execution_time', 'execution_location']
        extra_kwargs = {f: {'required': False} for f in fields}


# class AdAssignPerformerSerializer(serializers.Serializer):
#     performer_id = serializers.IntegerField()

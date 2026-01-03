from rest_framework import serializers
from .models import Ad


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = "__all__"
        read_only_fields = ["creator", "date_added", 'status', 'performer']

class AdCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'category']

class AdReadSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()
    performer = serializers.StringRelatedField()

    class Meta:
        model = Ad
        fields = "__all__"

class AdUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'category']
        read_only_fields = ['creator', 'date_added', 'status', 'performer']

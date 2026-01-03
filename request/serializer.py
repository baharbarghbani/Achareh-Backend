from rest_framework import serializers
from .models import Request

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = [
            "id",
            "performer",
            "ad",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "performer", "created_at", "status"]

class RequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ["ad"]
        read_only_fields = ["id"]

class RequestReadSerializer(serializers.ModelSerializer):
    performer = serializers.StringRelatedField()
    ad = serializers.StringRelatedField()

    class Meta:
        model = Request
        fields = [
            "id",
            "performer",
            "ad",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "performer", "created_at", "status"]


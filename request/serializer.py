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
        read_only_fields = ["performer", "created_at", "status"]
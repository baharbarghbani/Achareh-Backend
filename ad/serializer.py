from rest_framework import serializers
from .models import Ad, AdRequest
from rest_framework import serializers


class AdCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ["title", "description", "category"]

class AdReadSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()
    performer = serializers.StringRelatedField()

    class Meta:
        model = Ad
        fields = "__all__"




class AdUpdateSerializer(serializers.ModelSerializer):
    """
    Used for PATCH/PUT of normal Ad fields.
    Keep status/performer/creator read-only to prevent unauthorized transitions.
    """

    class Meta:
        model = Ad
        fields = [
            "title",
            "description",
            "category",
            "execution_time",
            "execution_location",
        ]
        read_only_fields = ["status", "performer", "creator", "date_added"]


class AdReadSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()
    performer = serializers.StringRelatedField()

    class Meta:
        model = Ad
        fields = "__all__"


class AdRequestCreateSerializer(serializers.ModelSerializer):
    """
    You are creating an AdRequest via URL context (ad_id) and current user.
    No body fields needed.
    """
    class Meta:
        model = AdRequest
        fields = []


class AdRequestReadSerializer(serializers.ModelSerializer):
    performer_id = serializers.IntegerField(source="performer.id", read_only=True)
    performer_username = serializers.CharField(source="performer.username", read_only=True)

    ad_id = serializers.IntegerField(source="ad.id", read_only=True)
    ad_title = serializers.CharField(source="ad.title", read_only=True)

    ad_status = serializers.CharField(source="ad.status", read_only=True)

    class Meta:
        model = AdRequest
        fields = [
            "id",
            "status",
            "created_at",
            "performer_id",
            "performer_username",
            "ad_id",
            "ad_title",
            "ad_status",
        ]
        read_only_fields = fields


class AdRatingSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    content = serializers.CharField(required=False, allow_blank=True)

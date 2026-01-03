from rest_framework import serializers
from .models import Ad, AdRequest


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
        fields = ["title", "description", "category", "execution_time", "execution_location"]
        read_only_fields = ["status", "performer", "creator", "date_added"]


class AdRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdRequest
        fields = []

class AdRequestReadSerializer(serializers.ModelSerializer):
    performer_id = serializers.IntegerField(source="performer.id", read_only=True)
    performer_username = serializers.CharField(source="performer.username", read_only=True)
    ad_id = serializers.IntegerField(source="ad.id", read_only=True)
    ad_title = serializers.CharField(source="ad.title", read_only=True)

    class Meta:
        model = AdRequest
        fields = ["id", "status", "created_at", "performer_id", "performer_username", "ad_id", "ad_title"]
        read_only_fields = fields
class AdRequestUpdateSerializer(serializers.Serializer):
    """
    One PATCH endpoint supports all transitions without touching Ad.status directly.

    Creator choose performer:
      {"status": "approved"} or {"status": "rejected"}

    Performer report done:
      {"done_reported": true}

    Creator confirm done:
      {"done_confirmed": true}
    """
    status = serializers.ChoiceField(
        choices=[AdRequest.Status.APPROVED, AdRequest.Status.REJECTED],
        required=False
    )
    done_reported = serializers.BooleanField(required=False)
    done_confirmed = serializers.BooleanField(required=False)

class AdRequestSerializer(serializers.ModelSerializer):
    ad = serializers.StringRelatedField()

    class Meta:
        model = AdRequest
        fields = ['ad', 'status', 'created_at', 'performer']
        read_only_fields = ["performer", "created_at", "ad", 'status"]']


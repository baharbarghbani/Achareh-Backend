from rest_framework import serializers
from .models import Ad, AdRequest

class AdCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ["title", "description", "category"]

class AdPatchSerializer(serializers.ModelSerializer):

    done_reported = serializers.BooleanField(required=False)
    done_confirmed = serializers.BooleanField(required=False)

    class Meta:
        model = Ad
        fields = [
            "done_reported",
            "done_confirmed",
        ]

    def validate(self, attrs):
        done_reported = "done_reported" in attrs
        done_confirmed = "done_confirmed" in attrs

        if done_reported and done_confirmed:
            raise serializers.ValidationError(
                "Send only one of done_reported or done_confirmed."
            )

        if done_reported and attrs["done_reported"] is not True:
            raise serializers.ValidationError({"done_reported": "Must be true."})

        if done_confirmed and attrs["done_confirmed"] is not True:
            raise serializers.ValidationError({"done_confirmed": "Must be true."})

        return attrs

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

    done_reported = serializers.SerializerMethodField()
    done_confirmed = serializers.SerializerMethodField()

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
            "done_reported",
            "done_confirmed",
        ]
        read_only_fields = fields

    def get_done_reported(self, obj):
        return obj.ad.status == Ad.Status.DONE_REPORTED

    def get_done_confirmed(self, obj):
        return obj.ad.status == Ad.Status.DONE


class AdRequestChooseSerializer(serializers.Serializer):
    choose = serializers.BooleanField()


class AdRatingSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    content = serializers.CharField(required=False, allow_blank=True)

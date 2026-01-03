from rest_framework import serializers
from .models import Ad, AdRequest


# =========================
# Ads
# =========================

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = "__all__"
        read_only_fields = ["creator", "date_added", "status", "performer"]


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

class AdRequestDoneReportedSerializer(serializers.Serializer):
    done_reported = serializers.BooleanField()


class AdRequestDoneConfirmedSerializer(serializers.Serializer):
    done_confirmed = serializers.BooleanField()

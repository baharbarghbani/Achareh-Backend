from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile


User = get_user_model()

class UserReadSerializer(serializers.ModelSerializer):
    roles = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'roles', 'first_name', 'last_name', 'phone_number']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone_number']

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()  # username OR email OR phone_number
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier", "").strip()
        password = attrs.get("password", "")

        user = User.objects.filter(
            Q(username__iexact=identifier) |
            Q(email__iexact=identifier) |
            Q(phone_number__iexact=identifier)
        ).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "User account is disabled."})

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": user,
        }


class ProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    class Meta:
        model = Profile
        fields = ['name', 'last_name', 'average_rating', 'ads_count', 'ads', 'comments']
        read_only_fields = ['name', 'last_name', 'average_rating', 'ads_count', 'ads', 'comments']


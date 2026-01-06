from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, ListAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsPerformer, IsCustomer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializer import UserReadSerializer, UserCreateSerializer, UserUpdateDeleteSerializer, LoginSerializer, PerformerProfileSerializer, CustomerProfileSerializer
from .models import Profile
from ad.models import Ad
from django.db import models
from .utils import is_performer
from rest_framework.exceptions import PermissionDenied


User = get_user_model()


from rest_framework.authtoken.models import Token

class UserRegisterAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = Token.objects.create(user=user)

        return Response(
            {"token": token.key, "user": UserReadSerializer(user).data},
            status=status.HTTP_201_CREATED
        )




class UserLoginAPIView(CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        access = serializer.validated_data["access"]
        refresh = serializer.validated_data["refresh"]

        return Response({
            "access": access,
            "refresh": refresh,
            "user": UserReadSerializer(user).data,
        }, status=status.HTTP_200_OK)




class UserMeAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateDeleteSerializer
        return UserReadSerializer


class UserListAPIView(ListAPIView):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserReadSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"detail": "Only admin can list users."}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)


class UserRetrieveDestroyAPIView(RetrieveAPIView, DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserReadSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"detail": "Only admin can view other users."}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"detail": "Only admin can delete users."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class PerformerProfileAPIView(RetrieveAPIView):
    serializer_class = PerformerProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "user_id"

    def get_queryset(self):
        return Profile.objects.select_related("user")

    def get_object(self):
        user_id = self.kwargs[self.lookup_url_kwarg]
        target_user = get_object_or_404(User, id=user_id)
        if not is_performer(target_user):
            raise PermissionDenied("کاربر خواسته شده پیمانکار نیست.")
        profile = get_object_or_404(self.get_queryset(), user_id=self.kwargs[self.lookup_url_kwarg])
        profile = profile.annotate(
            completed_ads=models.Count(
                'user__ads_performed',
                filter=models.Q(user__ads_performed__status=Ad.Status.DONE),
                distinct=True
            )
        ).first()

        if profile is None:
            from django.http import Http404
            raise Http404("Profile not found")

        return profile
class CustomerProfileAPIView(RetrieveAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated, IsCustomer]
    lookup_url_kwarg = "user_id"

    def get_queryset(self):
        return Profile.objects.select_related("user")

    def get_object(self):
        user_id = self.kwargs[self.lookup_url_kwarg]
        return get_object_or_404(self.get_queryset(), user_id=user_id)



from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, ListAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializer import UserReadSerializer, UserCreateSerializer, UserUpdateDeleteSerializer

User = get_user_model()


class UserRegisterAPIView(CreateAPIView):
    """
    POST /api/users/register/
    Public endpoint to create an account.
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]


class UserMeAPIView(RetrieveUpdateAPIView):
    """
    GET  /api/users/me/
    PATCH /api/users/me/
    Logged-in user can see and update their own profile.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateDeleteSerializer
        return UserReadSerializer


class UserListAPIView(ListAPIView):
    """
    GET /api/users/
    Admin-only: list all users.
    """
    queryset = User.objects.all().order_by("id")
    serializer_class = UserReadSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"detail": "Only admin can list users."}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)


class UserDetailAPIView(RetrieveAPIView):
    """
    GET /api/users/<id>/
    Admin-only: retrieve any user.
    """
    queryset = User.objects.all()
    serializer_class = UserReadSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"detail": "Only admin can view other users."}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)


class UserDeleteAPIView(DestroyAPIView):
    """
    DELETE /api/users/<id>/
    Admin-only: delete any user.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"detail": "Only admin can delete users."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

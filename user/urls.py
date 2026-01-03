from django.urls import path
from .views import (
    UserRegisterAPIView,
    UserMeAPIView,
    UserListAPIView,
    UserDetailAPIView,
    UserDeleteAPIView,
)

urlpatterns = [
    path("users/register/", UserRegisterAPIView.as_view(), name="user-register"),
    path("users/me/", UserMeAPIView.as_view(), name="user-me"),
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailAPIView.as_view(), name="user-detail"),
    path("users/<int:pk>/delete/", UserDeleteAPIView.as_view(), name="user-delete"),
]

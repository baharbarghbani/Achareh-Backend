from django.urls import path
from .views import (
    UserRegisterAPIView,
    UserMeAPIView,
    UserListAPIView,
    UserRetrieveDestroyAPIView
)

urlpatterns = [
    path("users/register/", UserRegisterAPIView.as_view(), name="user-register"),
    path("users/me/", UserMeAPIView.as_view(), name="user-me"),
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserRetrieveDestroyAPIView.as_view(), name="user-detail"),
]

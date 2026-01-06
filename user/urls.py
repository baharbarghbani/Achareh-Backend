from django.urls import path
from .views import (
    UserRegisterAPIView,
    UserLoginAPIView,
    UserMeAPIView,
    UserListAPIView,
    UserRetrieveDestroyAPIView,
    PerformerProfileAPIView
)

urlpatterns = [
    path("users/register/", UserRegisterAPIView.as_view(), name="user-register"),
    path("users/login/", UserLoginAPIView.as_view(), name="user-login"),
    path("users/me/", UserMeAPIView.as_view(), name="user-me"),
    path("users/profile/performer/<int:pk>/", PerformerProfileAPIView.as_view(), name="user-profile"),
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserRetrieveDestroyAPIView.as_view(), name="user-detail"),
]


from django.urls import path
from .views import (
    UserRegisterAPIView,
    UserLoginAPIView,
    UserMeAPIView,
    UserListAPIView,
    UserRetrieveDestroyAPIView,
    PerformerProfileAPIView,
    CustomerProfileAPIView,
    CustomerFilterAPIView
)

urlpatterns = [
    path("users/register/", UserRegisterAPIView.as_view(), name="user-register"),
    path("users/login/", UserLoginAPIView.as_view(), name="user-login"),
    path("users/me/", UserMeAPIView.as_view(), name="user-me"),
    path("users/profile/performer/<int:user_id>/", PerformerProfileAPIView.as_view(), name="user-profile"),
    path("users/profile/customer/<int:user_id>/", CustomerProfileAPIView.as_view(), name="customer-profile"),
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserRetrieveDestroyAPIView.as_view(), name="user-detail"),
    path(
        "users/filter/<int:base_rating>/<int:base_comments>/",
        CustomerFilterAPIView.as_view(),
        name="customer-filter",
    ),
]


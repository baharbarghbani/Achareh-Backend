from django.urls import path
from .views import (
    AdListCreateAPIView,
    AdRetrieveUpdateDestroyAPIView,
    AdRequestListCreateAPIView,
    AdRequestRetrieveUpdateAPIView,
    RequestListAPIView,
    OpenAdListAPIView,
)

urlpatterns = [
    path("ads/", AdListCreateAPIView.as_view()),
    path("ads/open/", OpenAdListAPIView.as_view()),
    path("ads/<int:pk>/", AdRetrieveUpdateDestroyAPIView.as_view()),
    path("ads/<int:pk>/requests/", AdRequestListCreateAPIView.as_view()),
    path("ads/<int:pk>/requests/<int:request_pk>/", AdRequestRetrieveUpdateAPIView.as_view()),
    path("ads/requests/", RequestListAPIView.as_view()),
]

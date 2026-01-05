from django.urls import path
from .views import (
    AdListCreateAPIView,
    AdRetrieveUpdateDestroyAPIView,
    OpenAdListAPIView,
    AdRequestListCreateAPIView,
    AdRequestRetrieveUpdateAPIView,
    RequestListAPIView,
    AdRatingAPIView,
)

urlpatterns = [
    # Ads
    path("ads/", AdListCreateAPIView.as_view()),
    path("ads/open/", OpenAdListAPIView.as_view()),
    path("ads/<int:pk>/", AdRetrieveUpdateDestroyAPIView.as_view()),

    # Requests nested under ads
    path("ads/<int:pk>/requests/", AdRequestListCreateAPIView.as_view()),
    path("ads/<int:pk>/requests/<int:request_pk>/", AdRequestRetrieveUpdateAPIView.as_view()),

    # Performer own requests
    path("ads/requests/", RequestListAPIView.as_view()),

    # Rating endpoint
    path("ads/<int:pk>/rate/", AdRatingAPIView.as_view()),
]

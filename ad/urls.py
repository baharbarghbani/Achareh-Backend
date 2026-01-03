from django.urls import path
from .views import AdListCreateAPIView, AdRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("ads/", AdListCreateAPIView.as_view()),
    path("ads/<int:pk>/", AdRetrieveUpdateDestroyAPIView.as_view()),
]

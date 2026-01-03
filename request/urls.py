from django.urls import path
from .views import RequestListCreateAPIView, RequestRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("requests/", RequestListCreateAPIView.as_view(), name="request-list-create"),
    path("requests/<int:pk>/", RequestRetrieveUpdateDestroyAPIView.as_view(), name="request-detail"),
]
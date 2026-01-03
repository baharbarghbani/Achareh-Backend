from django.urls import path
from .views import RequestListCreateDestroyAPIView, RequestRetrieveUpdateAPIView

urlpatterns = [
    path("requests/", RequestListCreateDestroyAPIView.as_view(), name="request-list-create"),
    path("requests/<int:pk>/", RequestRetrieveUpdateAPIView.as_view(), name="request-detail"),
]
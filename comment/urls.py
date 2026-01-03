from django.urls import path
from .views import CommentListCreateAPIView, CommentRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("comments/", CommentListCreateAPIView.as_view()),
    path("comments/<int:pk>/", CommentRetrieveUpdateDestroyAPIView.as_view()),
]
